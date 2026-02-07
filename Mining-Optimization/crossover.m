function [y1, y2]=crossover(x1,x2,varmin,varmax,gamma)

    alpha=unifrnd(-gamma,1+gamma,size(x1));
    
    y1=alpha.*x1+(1-alpha).*x2;
    y2=alpha.*x2+(1-alpha).*x1;
    
    y1=max(y1,varmin);
    y1=min(y1,varmax);
    
    y2=max(y2,varmin);
    y2=min(y2,varmax);

end