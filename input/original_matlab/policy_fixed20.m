function [action, mask_idx] = policy_fixed20(measured_state, cfg) %#ok<INUSD>
% Policy B uses the 20 MHz on subchannel 1 whenever it was last measured idle.
if measured_state(1) == 0
    action = 1;
    mask_idx = -1;  % Sentinel value for fixed 20 MHz
else
    action = 0;
    mask_idx = 0;
end
end
