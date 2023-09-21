## The dependencies in requirements need to be installed before use

### The installation command is: 
` pip install -r requirements.txt `

It is necessary to modify the files in pyomo to prevent it from outputting invalid log information.

The file path is: `"install path"/pyomo/core/base/PyomoModel.y` in line 260   
We change it as follows:
```
        # If there is a warning, then print a warning message.
        #
        if (results.solver.status == SolverStatus.warning):
            pass
            '''
            tc = getattr(results.solver, 'termination_condition', None)
            msg = getattr(results.solver, 'message', None)
            logger.warning(
                'Loading a SolverResults object with a '
                'warning status into model.name="%s";\n'
                '  - termination condition: %s\n'
                '  - message from solver: %s'
                % (instance.name, tc, msg))'''
        #
        # If the solver status not one of either OK or Warning, then
```

where "install path" is your python dependency install location. This is done by commenting out the invalid log output, because pyomo outputs this when the model run is infeasible, but there are many transshipment models in our method that are infeasible.

## Then we need to install GUROBI, I installed gurobi academic version, 
GUROBI website is [https://www.gurobi.com/]

If you want to install the academic version, then your network IP needs to be within the scope of the school, otherwise you need to apply for free IP verification [http://www.gurobi.cn/NewsView1.Asp?id=4]


## If you have succeeded in the above process, then we only need to run this program.

Branch and bound run command:   
 `python run.py`    
  

I saved the result files of the two of them in [PART1](/data/PART1/), [PPART1](/data/PPART1/) respectively.


## For four options I used the three case file instructions I calculated.
For [PART1](/data/PART1/), We can find TAC in the results1.csv file of the corresponding file directory of examples. 
Other data can be found from time_file.txt and the non-isothermal data you can find in [NPART1](/data/NPART1/) 

The data of other files is the data of the optimal structure saved, as well as the data generated during the running process so that we can track the running progress of the program.