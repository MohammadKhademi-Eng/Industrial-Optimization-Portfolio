clc;
clear;
close all;
tic

%% problem definition 

global NFE;
NFE=0;


FitnessFunction=@(n) NPV(n);


nvar=29;
varsize=[1 nvar];

varmin=0;
varmax=1;
best(1)=1;
%% GA Parameters

MaxIT=10; 

npop=10;
 
pc=0.8;
nc=2*round(pc*npop/2);

pm=0.3;
nm=round(pm*npop);

mu=0.1;

gamma=0.1;

%% initialization

empty_indivisal.position=[];
empty_indivisal.fitness=[];

pop=repmat(empty_indivisal,npop,1);

for i=1:npop
   
   pop(i).position=createrandomsolution();
   pop(i).fitness=FitnessFunction(pop(i).position);
   
end


fitnesses=[pop.fitness];
[fitnesses,sortorder]=sort(fitnesses,'descend');
pop=pop(sortorder);

Bestsol=pop(1);

Bestfitness=zeros(MaxIT,1);

nfe=zeros(MaxIT,1);

%% Main Loop

for it=1:MaxIT
   
    popc=repmat(empty_indivisal,nc/2,2);
    
    for k=1:nc/2
        
        
        i1=randi([1 npop]);
        p1=pop(i1);
        
        i2=randi([1 npop]);
        p2=pop(i2);
        
        [popc(k,1).position, popc(k,2).position]=crossover(p1.position,p2.position,gamma,varmin,varmax);
        
        popc(k,1).fitness=FitnessFunction(popc(k,1).position);
        popc(k,2).fitness=FitnessFunction(popc(k,2).position);
        
    end
    popc=popc(:);
    
    popm=repmat(empty_indivisal,nm,1);
    
    for k=1:nm
       
        i=randi([1 npop]);
        p=pop(i);
        
        popm(k).position=Mutate(p.position,mu,varmin,varmax);
        
        popm(k).fitness=FitnessFunction(popm(k).position);
        
         
    end
         
       pop=vertcat(pop,popc,popm);
       
       
       fitnesses=[pop.fitness];
       [fitnesses,sortorder]=sort(fitnesses,'descend');
       pop=pop(sortorder);
       
       
       pop=pop(1:npop);
       fitnesses=fitnesses(1:npop);
       
       
       Bestsol=pop(1);
       
       Bestfitness(it)=Bestsol.fitness;
       
       nfe(it)=NFE;    
       
       
       disp(['Iteration' num2str(it) ': Bestfitness ' num2str(Bestfitness(it))]);
    
end


toc
%% Result

figure;
plot(Bestfitness,'LineWidth',2);
xlabel('Iteration');
ylabel('fitness');