%# load data
load carsmall

%# construct predicting attributes and target class
vars = {'MPG' 'Cylinders' 'Horsepower' 'Model_Year'};
x = [MPG Cylinders Horsepower Model_Year];
y = cellstr(Origin);

%# train classification decision tree
t = classregtree(x, y, 'method','classification', 'names',vars, ...
                'categorical', [2 4], 'prune','off');
view(t)

%# test
yPredicted = eval(t, x);
cm = confusionmat(y,yPredicted);           %# confusion matrix
N = sum(cm(:));
err = ( N-sum(diag(cm)) ) / N;             %# testing error

%# prune tree to avoid overfitting
tt = prune(t, 'level',2);
view(tt)

%# predict a new unseen instance
inst = [33 4 78 NaN];
prediction = eval(tt, inst)
