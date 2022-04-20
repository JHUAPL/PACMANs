% Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
% All rights reserved.
% Distributed under the terms of the BSD 3-Clause License.

% YAMYLMatlab License
% Copyright (c) 2011 CTU in Prague and  Energocentrum PLUS s.r.o.
% Permission is hereby granted, free of charge, to any person
% obtaining a copy of this software and associated documentation
% files (the "Software"), to deal in the Software without
% restriction, including without limitation the rights to use,
% copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the
% Software is furnished to do so, subject to the following
% conditions:
% The above copyright notice and this permission notice shall be
% included in all copies or substantial portions of the Software.



yaml_file = './config.yaml'; 
yaml_path='C:/Matlab/repos/YAMLMatlab_0.4.3';

addpath(genpath(yaml_path));
ConfigStruct = ReadYaml(yaml_file); 

disp('yaml config read success')
