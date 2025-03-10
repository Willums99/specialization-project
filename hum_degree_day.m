function [dehumGD, humGD] = hum_degree_day(Toutavg,wout,Tbasemin,Tbasemax,RHbasemin,RHbasemax)
% Function to compute gram days.
% I/O: [dehumGD, humGD] = hum_degree_day(Toutavg,wout,Tbasemin,Tbasemax,RHbasemin,RHbasemax)
% input:  - Toutavg: outdoor temperature average in °C [1-by-1]
%         - wout: outdoor specific humidity in kg/kg [1-by-1]
%         - Tbasemin: minimum temperature threshold in °C [1-by-1] (in your case, let's use -50°C)
%         - Tbasemax: maximum temperature threshold in °C [1-by-1]
%         - RHbasemin: minimum relative humidity threshold in % [1-by-1]
%         - RHbasemax: maximum relative humidity threshold in % [1-by-1]
% output: - dehumGD: dehumidifying degree day in kg/kg [1-by-1]
%         - humGD: humidifying degree day in kg/kg [1-by-1]
%
% EXAMPLE: [dehumGD, humGD] = hum_degree_day(10,0.005,-50,15,30,50)

RHout = relative_humidity(Toutavg,wout);
DD = nan(365,1);

if Toutavg <= Tbasemax && Toutavg >= Tbasemin
    if RHout > RHbasemax
        win = specific_humidity(Toutavg,RHbasemax); % compute the indoor specific humidity
        DD = wout-win;
    elseif RHbasemin > RHout
        win = specific_humidity(Toutavg,RHbasemin); % compute the indoor specific humidity
        DD = wout-win;
    else
        DD = 0;
    end

elseif Toutavg > Tbasemax
    RHout = relative_humidity(Tbasemax,wout);
    if RHout > RHbasemax
        win = specific_humidity(Tbasemax,RHbasemax); % compute the indoor specific humidity
        DD = wout-win;
    elseif RHbasemin > RHout
        win = specific_humidity(Tbasemax,RHbasemin); % compute the indoor specific humidity
        DD = wout-win;
    else
        DD = 0;
    end

elseif Toutavg < Tbasemin
    RHout = relative_humidity(Tbasemin,wout);
    if RHout > RHbasemax
        win = specific_humidity(Tbasemin,RHbasemax); % compute the indoor specific humidity
        DD = wout-win;
    elseif RHbasemin > RHout
        win = specific_humidity(Tbasemin,RHbasemin); % compute the indoor specific humidity
        DD = wout-win;
    else
        DD = 0;
    end
end
 
humGD = DD; humGD(humGD>0) = 0; humGD = humGD*-1;
dehumGD = DD; dehumGD(dehumGD<0) = 0; dehumGD = dehumGD*1;

end