function y=Mutate(x,mu,varmin,varmax)

    nvar=numel(x);
    
    nmu=ceil(mu*nvar);
    
    j=randsample(nvar,nmu);
    
    sigma=0.1*(varmax-varmin);
    
    y=x;
    y(j)=x(j)+sigma*randn(size(j));
    
    y=max(y,varmin);
    y=min(y,varmax);

end