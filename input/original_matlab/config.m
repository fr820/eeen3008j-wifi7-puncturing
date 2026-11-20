function cfg = config()
% Central configuration. The report labels each parameter as measured, cited, or illustrative.
cfg.N_slots          = 10000;   % Number of simulation decision slots
cfg.num_subch        = 4;       % 80 MHz = 4 x 20 MHz
cfg.subch_bw         = 20;      % Bandwidth per subchannel (MHz)
cfg.num_busy         = 1;       % Number of potentially busy subchannels (1, 2, or 3)
cfg.duty             = 0.3;     % Interference duty cycle (0.1, 0.3, or 0.6)

cfg.T_probe          = 5;       % Take one measurement every five slots
cfg.probe_slots      = 0.2;     % Measurement cost of 0.2 slot per probe (illustrative)
cfg.sig_slots_per_mhz= 0.01;    % Signalling cost of 0.01 slot per MHz (illustrative)
cfg.bytes_per_mhz_slot = 1000;  % Delivery rate of 1,000 bytes per MHz per slot (illustrative)

% Stale measurement model. The probabilities are for an idle reading on a busy subchannel and a busy reading on an idle subchannel.
cfg.p_stale_idle     = 0.10;
cfg.p_stale_busy     = 0.20;

cfg.seed             = 1;

% Candidate 80 MHz masks in the prototype. 1 means active and 0 means punctured.
% 1111, 0111, 1011, 1101, 1110, 0011, 1100, 1001
cfg.allowed_masks = [ ...
    1 1 1 1; ...
    0 1 1 1; ...
    1 0 1 1; ...
    1 1 0 1; ...
    1 1 1 0; ...
    0 0 1 1; ...
    1 1 0 0; ...
    1 0 0 1  ...
    ];
end
