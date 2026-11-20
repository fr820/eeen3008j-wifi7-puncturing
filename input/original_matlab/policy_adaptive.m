function [action, mask_idx, U] = policy_adaptive(measured_state, cfg)
% Policy C uses the latest measurement to select the candidate mask with the highest utility (bandwidth times idle probability less signalling cost).
masks = cfg.allowed_masks;
num_masks = size(masks,1);
U = -inf(1, num_masks);

for i = 1:num_masks
    m = masks(i,:);
    B = sum(m) * cfg.subch_bw;
    if B == 0
        continue;
    end
    % Estimate the probability that all active subchannels are idle at transmission time.
    P_idle = 1;
    for k = find(m)
        if measured_state(k) == 0
            P_idle = P_idle * (1 - cfg.p_stale_idle);
        else
            P_idle = P_idle * cfg.p_stale_busy;
        end
    end
    sig = cfg.sig_slots_per_mhz * B;
    U(i) = B * P_idle - sig;   % Simplified utility. Total time includes the probing overhead.
end

[bestU, bestIdx] = max(U);
if bestU > 0
    action = 1;
    mask_idx = bestIdx;
else
    action = 0;
    mask_idx = 0;
end
end
