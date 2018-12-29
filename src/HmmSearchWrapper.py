"""
package com.epam.ubcg;
Source code recreated from a .class file by IntelliJ IDEA
(powered by Fernflower decompiler)
"""
'''
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
'''
from src.abc_program_wrapper import UtilWrapperABC
import os
import subprocess
import json

class Hmmsearch(UtilWrapperABC):
    """
    Wrapper to hmmsearch
    """
    def __init__(self, ProgramPath, inputFileName, CdsNucFileName, CdsProFileName):
        self.ProgramPath = ProgramPath
        self.inputFileName = inputFileName
        self.CdsNucFileName = CdsNucFileName
        self.CdsProFileName = CdsProFileName
        self.arguments = {}
        self.arguments.update({'ProgramPath': ProgramPath})   # self.arguments.add(ProgramPath);
        self.hmmProfileFile ={}
        self.seqdb = {}


    def run(self, file_path: str, **kwargs) -> None:
        """
        Method to execute hmmsearch
        :param path: some file here
        :kwargs: args to run program with
        :return:
        """
    def getHmmProfileFile(self):
        return self.hmmProfileFile

    def getSeqdb(self):
        return self.seqdb

    def geteValue(self):
        return self.eValue

    '''
    def setHmmProfileFile(self, hmmProfileFile):
        self.hmmProfileFile = hmmProfileFile
        self.arguments.update({'hmmProfileFile':hmmProfileFile})   #this.arguments.add(hmmProfileFile);

    def setSeqdb(self, seqdb):
        self.seqdb = seqdb
        self.arguments.update({'seqdb':seqdb})  #this.arguments.add(seqdb);

    def seteValue(self, eValue):
        self.eValue = eValue
        self.arguments.update({"-E":'-E'})
        self.arguments.update({"eValue":eValue})   #this.arguments.add(String.valueOf(eValue));

    def setNoAlignment(self):
        self.arguments.update({"--noali":"--noali"})

    def setTC(self):
        self.arguments.update({"--cut_tc":"--cut_tc"})

    def setThreads(self, threads):
        self.threads = threads
        self.arguments.update({"--cpu":"--cpu"})
        self.arguments.update({"threads": int(str(threads))}) #Integer.toString(threads));
'''

    def setParameters(self, hmmProfileFile, seqdb, eValue, threads):
        self.hmmProfileFile = hmmProfileFile
        self.seqdb = seqdb
        self.eValue = eValue
        self.threads = threads

    def executeToBuffer(self):
        #File output = null;
        output = open("hmmsearch.out", "w+");
        # try to run hmms and write result to output,
        process = subprocess.Popen(
            ['hmmsearch', '%s' % self.hmmProfileFile, '%s' % self.seqdb,
            '-E', '%s' % self.eValue, "--noali", "--noali",
            '--cut_tc', "--cpu", '%s' % self.threads, '%s' % "hmmsearch.out"])

            #Process hmmsearch = (new ProcessBuilder(this.arguments)).redirectOutput(output).start();
            #StreamGobbler stdError = new StreamGobbler(hmmsearch.getErrorStream(), (String)null, false);
            #stdError.start();
        process.wait()
        return output;


    def hmmsearchParserPipe(self, bcgDirectory, outputFile, metaDataList, CdsNucFileName, CdsProFileName, output):
        try:
            hmmFR = open(outputFile , 'r');
            seqList_dna = []    #DnaSeqDomainList - difference between it and list ?
            seqList_dna = open(CdsNucFileName).read().splitlines()    #seqList_dna.importFile(CdsNucFileName);
            #HashMap<Integer, Integer> hashDNA = new HashMap(); #will use [[valueOf(((DnaSeqDomain..)), i]]
            # how to ger title ? - need to import lib with DnaSeqDomainList

            for i in seqList_dna:
                hashDNA.put(Integer.valueOf(((DnaSeqDomain)seqList_dna.getList().get(i)).getTitle()), i);
            }

            DnaSeqDomainList seqList_protein = new DnaSeqDomainList();
            HashMap<Integer, Integer> hashProtein = new HashMap();
            seqList_protein.importFile(CdsProFileName);

            for(int i = 0; i < seqList_protein.getListSize(); ++i) {
                hashProtein.put(Integer.valueOf(((DnaSeqDomain)seqList_protein.getList().get(i)).getTitle()), i);
            }

            UbcgDomain ubcg = new UbcgDomain();
            ubcg.parseHmmoutFile(outputBR);
            HashMap<String, ArrayList<UbcgGeneDomain>> map = ubcg.getMap();
            if (map == null) {
                System.out.println("Error while extracting");
                return;
            }

            if (ubcg.getN_ubcg() == 0) {
                System.out.println("Warning no UBCGs were found");
            }

            Set<String> keys = map.keySet();
            Iterator itr = keys.iterator();

            while(itr.hasNext()) {
                String query = (String)itr.next();
                ArrayList<UbcgGeneDomain> list = (ArrayList)map.get(query);
                Iterator var20 = list.iterator();

                while(var20.hasNext()) {
                    UbcgGeneDomain cds = (UbcgGeneDomain)var20.next();
                    Integer index = (Integer)hashProtein.get(cds.getFeatureIndex());
                    cds.setDna(((DnaSeqDomain)seqList_dna.getList().get(index)).getSequence());
                    cds.setProtein(((DnaSeqDomain)seqList_protein.getList().get(index)).getSequence());
                }
            }

            this.writeJsonFilePipe(bcgDirectory, ubcg, output, metaDataList);
            hmmFR.close();
            outputBR.close();
            outputFile.delete();
        } catch (IOException var22) {
            System.err.println("Error : CDS fasta file is not available.");
            System.err.println(var22.getMessage());
            this.fileDeletion();
            System.exit(1);


    def addJsonObject(self, title, value):
        self.project_uid_obj = json.dumps({title: value})

    def writeJsonFilePipe(bcgDirectory,  ubcg, outputFileName, metaDataList):
        data = {
            "uid": metaDataList[0],
            "label": metaDataList[1],
            "accession": metaDataList[4],
            "taxon_name": metaDataList[2],
            "ncbi_name": None,
            "strain_name": metaDataList[3],
            "strain_type": metaDataList[5],
            "strain_property": None,
            "taxonomy": metaDataList[6],
            "UBCG_target_gene_number|version": "92|v3.0",
            "n_ubcg": ubcg.getN_ubcg(),
            "n_genes": ubcg.getN_genes(),
            "n_paralog_ubcg": ubcg.getN_paralog_ubcg()}
        json.dumps(data)
        print ("Number of UBCGs: " + ubcg.getN_ubcg())
        print ("Total length of UBCGs: " + ubcg.getTotalLength_DNA())
        #dataObject
        var10 = UbcgDomain.UBCG
        var9 = UbcgDomain.UBCG.length
        for var8 in range(0, var9):
            query = var10[var8]
            ArrayList<UbcgGeneDomain> ubcgList = (ArrayList)ubcg.getMap().get(query);
            # JSONArray arr;
            if (ubcgList == null) {
                arr = new JSONArray();
                arr.add(0);
                dataObject.put(query, arr);
            } else {
                arr = new JSONArray();
                arr.add(ubcgList.size());

                for(int i = 0; i < ubcgList.size(); ++i) {
                    UbcgGeneDomain hit = (UbcgGeneDomain)ubcgList.get(i);
                    JSONArray hitarr = new JSONArray();
                    hitarr.add(hit.getFeatureIndex());
                    hitarr.add(hit.getDna());
                    hitarr.add(hit.getProtein());
                    hitarr.add(String.valueOf(hit.getEvalue()));
                    arr.add(hitarr);
                }

                dataObject.put(query, arr);
            }
        }

        JSONObject obj5 = new JSONObject();
        JSONObject data_structure = new JSONObject();
        JSONArray header = new JSONArray();
        header.add("n_genes");
        JSONArray headerhit = new JSONArray();
        headerhit.add("feature_index");
        headerhit.add("dna");
        headerhit.add("protein");
        headerhit.add("evalue");
        header.add(headerhit);
        data_structure.put("gene_name", header);
        obj5.put("data_structure", data_structure);
        json.add(obj5);
        JSONObject obj6 = new JSONObject();
        obj6.put("data", dataObject);
        json.add(obj6);

        try {
            FileWriter fwJson = new FileWriter(bcgDirectory + outputFileName + ".bcg");
            fwJson.write(json.toString());
            fwJson.flush();
            fwJson.close();
        } catch (IOException var16) {
            System.err.println(var16.getMessage());
            System.exit(1);
        }

    }

    ''' 
    do not delet, so can  check
     fileDeletion() {
        File prodigalOut = new File(this.inputFileName + "_prodigal.out");
        prodigalOut.delete();
        File CdsNucFile = new File(this.CdsNucFileName);
        CdsNucFile.delete();
        File CdsProFile = new File(this.CdsProFileName);
        CdsProFile.delete();
    }
}
