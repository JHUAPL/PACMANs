function [transient,monotonicState,lambda] = boxMneval(M_n)
%boxMneval uses the M_n (northern overturning) timeseries from the
%fourbox_Aredi box model and returns the number in the transient, whether
%the series is monotonic, and the restoration rate of the transient
%   
holdvar=find(abs(diff(M_n))>6e2,1,'last');
    if ~isempty(holdvar)
    transient=holdvar;
    else
        if sum(abs(diff(M_n))<1e3)==N-1
            transient=1;
        else
            transient=N;
        end
    end


    holdvar=diff(M_n(1:transient));
    if sum(holdvar>=0)==transient-1
        monotonicState=1;
        f1=fit([1:transient].',M_n(1:transient)-M_n(transient),'exp1');
        lambda=f1.b;
    elseif sum(holdvar<=0)==transient-1
        monotonicState=-1;
        f1=fit([1:transient].',M_n(1:transient)-M_n(transient),'exp1');
        lambda=f1.b;
    else
        monotonicState=0;
        finalapproach=find(sign(holdvar).*sign(holdvar(end))==-1,1,'last');
        f1=fit([finalapproach:transient].', M_n(finalapproach:transient)-M_n(transient),'exp1');
        lambda=f1.b;
    end
end