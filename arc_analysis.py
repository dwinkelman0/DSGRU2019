# -*- coding: utf-8 -*-
"""
arc_analysis.py
Daniel Winkelman
March 28, 2019
"""

import csv
import pprint
from os import getcwd
import sys

def csv_to_dicts(fname):
    with open(fname, encoding='ISO-8859-1') as file:
        reader = csv.DictReader(file)
        return [line for line in reader]
    
def select(values, *conditions):
    return [i for i in values if all([i[key] == value for key, value in conditions])]
    

# List of majors
def majors(entries, fout=None):
    majors = {}
    for entry in entries:
        majors[entry["Q4"]] = majors.get(entry["Q4"], 0) + 1
    
    if fout == None:
        iostream = sys.stdout
    else:
        iostream = open(fout, "w")
    for major, freq in sorted(majors.items(), key=lambda x: x[0].lower()):
        print("{1:2d}: {0:s}".format(major.lower(), freq), file=iostream)
    if fout != None:
        iostream.close()
        
    return majors

def filter_entries(entries, field):
    output = {}
    for entry in entries:
        for choice in entry[field].split(","):
            output[choice] = output.get(choice, []) + [entry]
        
    return output

# Run scripts
if __name__ == "__main__":
    values = csv_to_dicts("{0:s}/{1:s}".format(getcwd(), "arc_aac_data.csv"))
    finished = select(values, ("Finished", "1"), ("DistributionChannel", "anonymous"))

    majors(finished, "majors.txt")
    
    # Total number of completed responses
    filter_use_arc = filter_entries(finished, "Q17")
    print("{0:d} completed responses".format(len(finished)))
    print()
    
    # Filter completed responses into used ARC and not used ARC
    used_arc = filter_use_arc["1"]
    not_used_arc = filter_use_arc["2"]
    print("{0:d} students used ARC resources".format(len(used_arc)))
    print("{0:d} students did not use ARC resources".format(len(not_used_arc)))
    print()
    
    # Filter based on uses (same row counted as multiple uses)
    filter_uses = filter_entries(used_arc, "Q23")
    service_keys = {
            "1": "Group Tutoring",
            "2": "Drop-in Tutoring",
            "3": "Math Study Groups",
            "4": "Other Tutoring",
            "5": "Learning Consultations",
            "6": "SAGE",
            "": "Other"}
        
    goodness_keys = {
            "1": "Greatly",
            "2": "Moderately",
            "3": "No significant improvement",
            "4": "Negatively"}
    
    # Tutoring type services
    for k, v in filter_uses.items():
        if k in ["1", "2", "3", "4", "6"]:
            avg = sum([float(entry["Q25_1"]) for entry in v])/len(v)
            filter_conf = filter_entries(v, "Q19")
            print("{0:>30s}: {1:2d} samples".format(service_keys[k], len(v)))
            print("{0:>30s} +{1:.2f} Grade impact".format("", avg))
            for kc, vc in sorted(filter_conf.items(), key=lambda x: x[0]):
                print("{0:>30s}   * {2:2d} {1:s}".format("", goodness_keys[kc], len(vc)))
            print()
            
    # Learning consultation type services
    lc_users = filter_uses["5"]
    print("{0:>30s}: {1:2d} samples".format(service_keys["5"], len(lc_users)))
    
    filter_qol = filter_entries(lc_users, "Q26")
    print("{0:>30s} Quality of Life".format(""))
    for kc, vc in sorted(filter_qol.items(), key=lambda x: x[0]):
        print("{0:>30s}   * {2:2d} {1:s}".format("", goodness_keys[kc], len(vc)))
        
    filter_tm = filter_entries(lc_users, "Q28")
    print("{0:>30s} Time Management".format(""))
    for kc, vc in sorted(filter_tm.items(), key=lambda x: x[0]):
        print("{0:>30s}   * {2:2d} {1:s}".format("", goodness_keys[kc], len(vc)))
    print()
        
    # Recommended to other students
    filter_recommended = filter_entries(used_arc, "Q14")
    print("{0:d} students recommended ARC resources to other students".format(len(filter_recommended["1"])))
    print("{0:d} students did not recommend ARC resources to other students".format(len(filter_recommended["2"])))
    print()
    
    # Reason for initially going
    reason_keys = {
            "1": "Recommendation from student",
            "2": "Recommendation from faculty",
            "3": "Advertising by the ARC",
            "4": "Other"}
    filter_reason = filter_entries(used_arc, "Q13")
    print("Reasons for initially going to ARC")
    for k, v in sorted(filter_reason.items(), key=lambda x: x[0]):
        if k == "": continue
        print(" * {0:2d}: {1:s}".format(len(v), reason_keys[k]))
    print()
    
    # Students who were referred by other students who recommended it to other students
    double_recommend = filter_entries(filter_recommended["1"], "Q13")["1"]
    print("{0:2d} students were recommended to the ARC by other students and, in turn, recommended other students to the ARC".format(len(double_recommend)))
    print()
    
    # Reasons students did not go to ARC
    reason_not_keys = {
            "1": "Have not had time",
            "2": "Do not find them necessary",
            "3": "Do not offer resources for my coursework",
            "4": "Not aware of resources",
            "5": "Negative reputation of ARC",
            "6": "Other"}
    filter_reason_not = filter_entries(not_used_arc, "Q20")
    print("Reasons for not going to ARC")
    for k, v in sorted(filter_reason_not.items(), key=lambda x: x[0]):
        if k == "": continue
        print(" * {0:2d}: {1:s}".format(len(v), reason_not_keys[k]))
    print()
        
    # Utilization among TAs/peer tutors
    tutors_used = filter_entries(used_arc, "Q15")["1"]
    tutors_not_used = filter_entries(not_used_arc, "Q15")["1"]
    print("{0:d} TA's or peer tutors used ARC resources".format(len(tutors_used)))
    print("{0:d} TA's or peer tutors did not use ARC resources".format(len(tutors_not_used)))
    print()
    
    # People who know what the services are
    print("Students who understand what each service does")
    for k in "123456":
        filter_understand = filter_entries(finished, "Q12#1_{0:s}".format(k))
        print(" * Yes: {0:2d} / No: {1:2d}: {2:s}".format(
                len(filter_understand["1"]),
                len(filter_understand["2"]),
                service_keys[k]))
    print()
    
    # People who have seen ARC presentationa
    filter_pres = filter_entries(finished, "Q29")
    print("{0:d} students have seen an ARC presentation".format(len(filter_pres["1"])))
    print("{0:d} students have not seen an ARC presentation".format(len(filter_pres["2"])))