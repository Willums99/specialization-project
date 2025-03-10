function w = specific_humidity(T,RH)
% Function to compute specific humidity in kg/kg.
% I/O: w = specific_humidity(T,RH)
% input:  - T: temperature in °C [1-by-1]
%         - RH: relative humidity humidity in % [1-by-1]
% output: - w: specific humidity in kg/kg [1-by-1]

P = 101.325;
rh = RH/100;
es = saturated_pressure(T);
w = (0.622*rh*es)/(P-(rh*es));

end