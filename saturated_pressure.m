function es = saturated_pressure(T)
% Function to compute saturated pressure in kPa.
% I/O: es = saturated_pressure(T)
% input:  - T: temperature in °C [1-by-1]
% output: - es: saturated pressure in kPa [1-by-1]

if T > 0
    es = 0.61078*exp((17.27*T)/(237.3+T));
else
    es = 0.61078*exp((21.875*T)/(265.5+T));
end

end