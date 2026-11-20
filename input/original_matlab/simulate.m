function res = simulate(cfg, state, policy_name)
% Simulate slot decisions, periodic probing, transmissions, waiting, and overhead accounting.
N = cfg.N_slots;
measured = zeros(1, cfg.num_subch);
last_probe = -inf;

success_bytes = 0;
tx_count = 0;
fail_count = 0;
wait_count = 0;
probe_overhead = 0;
sig_overhead = 0;

wait_run = 0;
wait_runs = [];

for t = 1:N
    % Measurement
    if t - last_probe >= cfg.T_probe
        measured = state(t,:);
        last_probe = t;
        probe_overhead = probe_overhead + cfg.probe_slots;
    end

    % Policy decision
    switch policy_name
        case 'wait_all'
            [action, mask_idx] = policy_wait_all(measured, cfg);
        case 'fixed20'
            [action, mask_idx] = policy_fixed20(measured, cfg);
        case 'adaptive'
            [action, mask_idx] = policy_adaptive(measured, cfg);
        otherwise
            error('Unknown policy');
    end

    % Waiting
    if action == 0
        wait_count = wait_count + 1;
        wait_run = wait_run + 1;
        continue;
    end

    % Transmission
    if wait_run > 0
        wait_runs(end+1) = wait_run; %#ok<AGROW>
        wait_run = 0;
    end

    tx_count = tx_count + 1;

    if strcmp(policy_name, 'fixed20')
        m = [1 0 0 0];
        B = 20;
        sig = cfg.sig_slots_per_mhz * B;
    else
        m = cfg.allowed_masks(mask_idx,:);
        B = sum(m) * cfg.subch_bw;
        sig = cfg.sig_slots_per_mhz * B;
    end
    sig_overhead = sig_overhead + sig;

    % Use the actual transmission-time state. A busy active subchannel causes failure.
    active = find(m);
    if any(state(t, active) == 1)
        fail_count = fail_count + 1;
        success = 0;
    else
        success = 1;
        success_bytes = success_bytes + B * cfg.bytes_per_mhz_slot;
    end
end

if wait_run > 0
    wait_runs(end+1) = wait_run;
end

total_time = N + probe_overhead + sig_overhead;  % Equivalent number of slots
res.goodput_Mbps = success_bytes / total_time * 8 / 1000; % Convert to Mbps for 1 ms slots
res.success_bytes = success_bytes;
res.total_time = total_time;
res.tx_count = tx_count;
res.fail_rate = fail_count / max(tx_count,1);
res.wait_count = wait_count;
res.wait_mean = mean(wait_runs);
res.wait_p95 = simple_prctile(wait_runs, 95);
res.probe_overhead = probe_overhead;
res.sig_overhead = sig_overhead;
end
