import numpy

from deap import algorithms
from deap import base
from deap import cma
from deap import creator
from deap import tools

#from scoop import futures

import sframe
from parametering.ParameterUtil import ParameterUtil
from parametering.Parameterization import Parameterization
from formating.FormatingDataSets import FormatingDataSets
import numpy



class SFrame:
    
    #util = ParameterUtil(parameter_file = 'data/configuration/arxiv/exemplo_1994_1999/CombinationLinear/configToAG.txt')
    #util = ParameterUtil(parameter_file = 'data/configuration/arxiv/condmat_1994_1999/CombinationLinear/configToAG.txt')
    util = ParameterUtil(parameter_file = 'data/configuration/arxiv/astroph_1994_1999/CombinationLinear/configTOAG.txt')
    
    
    myparams = Parameterization(t0 = util.t0, t0_ = util.t0_, t1 = util.t1, t1_ = util.t1_, linear_combination=util.linear_combination,
                                filePathGraph = util.graph_file, filePathTrainingGraph = util.trainnig_graph_file, filePathTestGraph = util.test_graph_file, decay = util.decay, domain_decay = util.domain_decay, min_edges = util.min_edges, scoreChoiced = util.ScoresChoiced, weightsChoiced = util.WeightsChoiced, weightedScoresChoiced = util.WeightedScoresChoiced, FullGraph = None, result_random_file=util.result_random_file)
     
    metrics = sframe.SFrame.read_csv(FormatingDataSets.get_abs_file_path(util.calculated_file+'_normalizated.csv'))
    results = sframe.SFrame.read_csv(FormatingDataSets.get_abs_file_path(util.result_random_file))

    top = 20
    
    def __init__(self):
        pass
        

    @classmethod
    def evaluate(cls, individual):
        new_metric = float(0)
        ##print 'individuos: ', individual
        
        for index_score in  range(len(cls.myparams.ScoresChoiced)):
            #print cls.myparams.ScoresChoiced[index_score][0].getName()
            valorMetrica = cls.metrics[ cls.myparams.ScoresChoiced[index_score][0].getName() ]
            valorIndividual = individual[index_score]
            #print "valores ", valorMetrica, valorIndividual
            new_metric = new_metric + (valorMetrica * valorIndividual )
               
        ##print 'nova metrica',  new_metric
        copy_metrics = cls.metrics.copy()
        copy_metrics.add_column(new_metric, name='new_metric')
        copy_metrics = copy_metrics.topk('new_metric', k=cls.top)
        #print 'metrics after topk \n\n', copy_metrics
        copy_results = cls.results.copy()
        
        #print 'copy_results before join', copy_results
        copy_metrics = copy_metrics.join(copy_results)
        #print 'metrics after join \n\n', copy_metrics
        copy_metrics = copy_metrics.sort('new_metric', ascending=False)
        ##print 'copy metrics ', copy_metrics
        aux = [0]
        
        copy_metrics = copy_metrics.filter_by(aux,'result')
        zero = copy_metrics.num_rows()
        #print 'zero', zero
        del copy_metrics
        del copy_results
        result =  float(zero) / cls.top,
        #print 'resultado ', result
        return result



# Problem size
#N=8
N=len(SFrame.myparams.ScoresChoiced)

# -1 means we are approaching a minimization problem
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # , must be used because deap is used for multi-obj optm
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("evaluate", SFrame.evaluate)
#toolbox.register("map", futures.map)


def main():
    
    # to generate the aleatory values we need a seed
    numpy.random.seed(128)
    file1 = open('config.txt', 'r')
    line = file1.readline()
    line = line.strip('\n').strip('\r').split(',')
    SFrame.top = int(line[2])
    strategy = cma.Strategy(centroid=[5.0]*N, sigma=float(line[0]), lambda_=int(line[1]))
    
    toolbox.register("generate", strategy.generate, creator.Individual)
    toolbox.register("update", strategy.update)

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    algorithms.eaGenerateUpdate(toolbox, ngen=int(line[3]), stats=stats, halloffame=hof, verbose=True)
    file1.close()
    output = open('output.txt', 'w')
    for item in hof[0]:
        output.write("%s," % item)
    output.close()
if __name__ == "__main__":
    main()