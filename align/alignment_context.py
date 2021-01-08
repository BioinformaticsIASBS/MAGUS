'''
Created on Dec 4, 2020

@author: Vlad
'''

import os
from helpers import sequenceutils
from tasks import task
from configuration import Configs

class AlignmentContext:
    
    def __init__(self, **kwargs):
        self.outputFile = None
        self.workingDir = None
        self.sequencesPath = None
        self.subsetPaths = []
        self.subalignmentPaths = []
        self.backbonePaths = []
        self.guideTreePath = None
        
        self.unalignedSequences = None
        #self.taxa = []
        self.subsets = []
        self.subalignments = []
        self.taxonSubsetMap = {}
        self.taxonSubalignmentMap = {}
                
        self.backboneTaxa = {}
        self.backboneExtend = set()
        self.backboneSubalignment = {}
        
        self.subalignmentTasks = []
        self.backboneTasks = []
        self.graph = None
        
        for attr in kwargs:
            vars(self)[attr] = kwargs.get(attr)
        
        if not os.path.exists(self.workingDir):
            os.makedirs(self.workingDir)
    
    def awaitSubalignments(self):
        task.awaitTasks(self.subalignmentTasks)
    
    def initializeSequences(self):
        self.unalignedSequences = {}
        for i, subsetPath in enumerate(self.subsetPaths):
            self.subsets.append([])
            subset = sequenceutils.readFromFastaOrdered(subsetPath, removeDashes=True)
            for sequence in subset:
                self.unalignedSequences[sequence.tag] = sequence
                self.taxonSubsetMap[sequence.tag] = i
                self.subsets[i].append(sequence.tag)
        
        if Configs.constrain:
            self.subalignments = self.subsets
            self.taxonSubalignmentMap = self.taxonSubsetMap
        else:
            for s in self.subsets:
                for taxon in s:
                    self.taxonSubalignmentMap[taxon] = len(self.subalignments)
                    self.subalignments.append([taxon])
                
    def initializeBackboneSequenceMapping(self):
        if len(self.backboneTaxa) == 0:
            backboneSubsetTaxonMap = {i : subset for i, subset in enumerate(self.subsets)}
        else:
            backboneSubsetTaxonMap = {}
            for taxon in self.backboneTaxa:
                i = self.taxonSubsetMap[taxon]
                backboneSubsetTaxonMap[i] = backboneSubsetTaxonMap.get(i, [])
                backboneSubsetTaxonMap[i].append(taxon) 
        
        if Configs.constrain:
            for i, subalignPath in enumerate(self.subalignmentPaths):
                subalignment = sequenceutils.readFromFasta(subalignPath, removeDashes=False)
                for taxon in backboneSubsetTaxonMap.get(i, []):
                    self.backboneSubalignment[taxon] = subalignment[taxon]
        else:
            self.backboneSubalignment = self.unalignedSequences
    