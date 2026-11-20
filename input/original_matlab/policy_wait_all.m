function [action, mask_idx] = policy_wait_all(measured_state, cfg) %#ok<INUSD>
% Policy A transmits on all 80 MHz when the latest measurement shows all four subchannels idle. Otherwise it waits.
if all(measured_state == 0)
    action = 1;
    mask_idx = 1;   % 1111
else
    action = 0;
    mask_idx = 0;
end
end
