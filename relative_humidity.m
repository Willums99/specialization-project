function RH = relative_humidity(T,w)
% Function to compute relative humidity in %.
% I/O: RH = relative_humidity(T,w)
% input:  - T: temperature in °C [1-by-1]
%         - w: specific humidity humidity in kg/kg [1-by-1]
% output: - RH: relative humidity in % [1-by-1]

P = 101.325;
es = saturated_pressure(T);
RH = (P*w)/(0.622+w)/es*100;

end