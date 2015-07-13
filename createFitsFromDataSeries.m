function [fitresult, gof] = createFitsFromDataSeries(paresXY_categorias,tipoDeAjuste)
%%CREATEFITSFROMDATASERIES Genera ajustes de curvas 
%   Entrada: Categorias, lista de celdas con nombres de pares
%   Entrada: lista de pares de vector columna X1,Y1,X2,Y2,...Xn,Yn
%   Salida: [fitresult, gof], fitresult es la lista con los modelos, 
%   gof es la lista con los parámetros de ajuste.
paresXY             =   paresXY_categorias(1:end-1);
categorias          =   paresXY_categorias{end};
if nargin<2
    tipoDeAjuste    =   'power2';
end
if mod(size(paresXY,1),2)==0 && numel(categorias)==size(paresXY,1)/2
    numberOfDataLists...
                    =   size(paresXY,1); % nargin;
    nDataPairs      =   numberOfDataLists/2;
    paresXY         =   reshape(paresXY,2,nDataPairs)';
    keepGoing       =   true;
    for i=1:nDataPairs
        keepGoing   =   keepGoing && ...
            all(numel(paresXY{i,1})==cellfun(@numel,paresXY(i,:)));
    end
end
if keepGoing
    %% Initialization.
    
    % Initialize arrays to store fits and goodness-of-fit
    fitresult = cell( nDataPairs, 1 );
    gof = struct( 'sse', cell( nDataPairs, 1 ), ...
        'rsquare', [], 'dfe', [], 'adjrsquare', [], 'rmse', [] );
    % Initialize plot handles.
    axesHandles=zeros(nDataPairs,1)*NaN;
    figure( 'Name', ...
        cell2mat(cellfun(@(x)[x,','],...
        categorias,'UniformOutput', false)'));
    
    %% Fit: Loop through list of pairs
    
    % Set up fittype and options.
    ft           = fittype( tipoDeAjuste );
    variables    = coeffnames(ft);
    opts = fitoptions( ft );
    opts.Display = 'Off';
    opts.Lower = [-Inf -Inf -Inf];
    %opts.StartPoint = [0,0,0];
    opts.Upper = [Inf Inf Inf];
    
    for i=1:nDataPairs
        % Fit model to data.
        [xData, yData] = ...
            prepareCurveData( paresXY{i,1}, paresXY{i,2} );
        xData(xData==0)=eps;
        [fitresult{i}, gof(i)] = ...
            fit( xData(xData>0), yData(xData>0),ft, opts );        
        % Plot fit with data.        
        axesHandles(i)=subplot(ceil(nDataPairs/2),2,i);
        h = plot( fitresult{i}, xData, yData, 'predobs', 0.9 );        
        % Label axes
        xlabel( ['X_{',categorias{i},'} (days)'] );
        ylabel( ['Y_{',categorias{i},'} (mm)'] );
        xlim([0,max(unique(vertcat(paresXY{:,1})))]);
        ylim([0,max(unique(vertcat(paresXY{:,2})))]);
        legend( h(1:3), {categorias{i}, 'FIT','Bounds'},...
            'Location', 'NorthEast');
        grid on;
    end
    filename    = strcat('exported_fit_params_',...
        [cell2mat(cellfun(@(x){strcat(x,'_')},...
        variables(1:end-1)')),variables{end}],...
        '.csv');
    headers     = ...
        [variables','R^2'];
    fid = fopen(filename,'w');
    fprintf(fid,'%s\n',formula(ft));
    fprintf(fid,'%s,','');
    fprintf(fid,'%s,',headers{1:end-1});
    fprintf(fid,'%s\n',headers{end});
    for i=1:nDataPairs
        coeffsToSave = coeffvalues(fitresult{i});
        fprintf(fid,'%s,',categorias{i});
        fprintf(fid,'%f,',coeffsToSave(1:end));
        fprintf(fid,'%f\n',gof(i).rsquare);
    end
    fclose(fid);
end
end