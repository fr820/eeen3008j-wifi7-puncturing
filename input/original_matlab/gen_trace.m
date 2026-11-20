function state = gen_trace(cfg)
% state(t,k) is 1 if subchannel k is busy in slot t and 0 if it is idle.
rng(cfg.seed);
state = zeros(cfg.N_slots, cfg.num_subch);
for t = 1:cfg.N_slots
    if cfg.num_busy == 0
        continue;
    end
    idx = randperm(cfg.num_subch, cfg.num_busy);  % Subchannels that may be busy in this slot
    for k = idx
        if rand() < cfg.duty
            state(t,k) = 1;
        end
    end
end
end
