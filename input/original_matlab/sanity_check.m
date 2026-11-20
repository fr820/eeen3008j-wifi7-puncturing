clear; clc;
cfg = config();

% No interference. With num_busy and duty both zero, every subchannel is idle.
cfg.num_busy = 0;
cfg.duty = 0;
cfg.seed = 1;
state = zeros(cfg.N_slots, cfg.num_subch);

res_wait = simulate(cfg, state, 'wait_all');
res_fix  = simulate(cfg, state, 'fixed20');
res_adap = simulate(cfg, state, 'adaptive');

fprintf('No interference sanity check:\n');
fprintf('  wait_all (80 MHz): %.1f Mbps\n', res_wait.goodput_Mbps);
fprintf('  fixed20 (20 MHz):  %.1f Mbps\n', res_fix.goodput_Mbps);
fprintf('  adaptive:          %.1f Mbps\n', res_adap.goodput_Mbps);
fprintf('  ratio wait_all/fixed20 = %.2f (expected ~4 minus overhead)\n', ...
    res_wait.goodput_Mbps / res_fix.goodput_Mbps);
