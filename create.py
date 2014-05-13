#!/usr/bin/env python3
import os
import sys
sys.path.append("scripts")

import classy_revy as cr
import setup_functions as sf
import converters as cv
from tex import TeX
from pdf import PDF
           

def create_material_pdfs(revue):
    file_list = []
    for act in revue.acts:
        for material in act.materials:
            file_list.append(material.path)

    conv = cv.Converter(revue.conf)
    conv.parallel_textopdf(file_list)

def create_individual_pdfs(revue):
    path = revue.conf["Paths"]
    
    # Create front pages for individual actors, if they don't already exist:
    frontpages_list = []
    if not os.path.exists(os.path.join(path["pdf"], "cache")):
        os.mkdir(os.path.join(path["pdf"], "cache"))

    for actor in revue.actors:
        file_name = "forside-{}.pdf".format(actor.name)
        if not os.path.isfile(os.path.join(path["pdf"], "cache", file_name)):
            tex = TeX(revue)
            tex.create_frontpage(subtitle=actor.name)
            frontpages_list.append([tex, file_name]) 

    # Create front pages:
    conv = cv.Converter(revue.conf)
    conv.parallel_textopdf(frontpages_list, outputdir=os.path.join(path["pdf"], "cache"))

    total_list = []
    for actor in revue.actors:
        #individual_list = (os.path.join(path["pdf"],"forside.pdf"), 
        individual_list = (os.path.join(path["pdf"],"cache", "forside-{}.pdf".format(actor.name)), 
                             os.path.join(path["pdf"],"aktoversigt.pdf"), 
                             os.path.join(path["pdf"],"rolleliste.pdf"),
                             actor,
                             os.path.join(path["pdf"],"rekvisitliste.pdf"))
        total_list.append((individual_list, 
                           os.path.join(path["individual pdf"],
                                       "{}.pdf".format(actor.name))))

    pdf = PDF(revue.conf)
    pdf.parallel_pdfmerge(total_list)


def create_song_manus_pdf(revue):
    path = revue.conf["Paths"]

    # Create front page, if it doesn't already exist:
    if not os.path.exists(os.path.join(path["pdf"], "cache")):
        os.mkdir(os.path.join(path["pdf"], "cache"))

    if not os.path.isfile(os.path.join(path["pdf"], "cache", "forside-sangmanuskript.pdf")):
            tex = TeX(revue)
            tex.create_frontpage(subtitle="sangmanuskript")
            tex.topdf("forside-sangmanuskript.pdf", outputdir=os.path.join(path["pdf"], "cache"))

    # Create song manuscript:
    file_list = [os.path.join(path["pdf"], "cache", "forside-sangmanuskript.pdf")]
    for act in revue.acts:
        for material in act.materials:
            if material.category == path["songs"]:
                file_list.append(os.path.join(path["pdf"], path["songs"],
                                        "{}.pdf".format(material.file_name[:-4])))
    
    pdf = PDF(revue.conf)
    pdf.pdfmerge(file_list, os.path.join(path["pdf"],"sangmanuskript.pdf"))


def create_parts(revue, args):
    tex = TeX(revue)

    if "aktoversigt" in args:
        tex.create_act_outline()
        tex.topdf("aktoversigt.pdf")

    elif "roles" in args:
        tex.create_role_overview()
        tex.topdf("rolleliste.pdf")

    elif "material" in args:
        create_material_pdfs(revue)

    elif "frontpage" in args:
        tex.create_frontpage()
        tex.topdf("forside.pdf")
    
    elif "props" in args:
        tex.create_props_list()
        tex.topdf("rekvisitliste.pdf")

    elif "individual" in args:
        create_individual_pdfs(revue)

    elif "contacts" in args:
        tex.create_contacts_list("contacts.csv")
        tex.topdf("kontaktliste.pdf")

    elif "songmanus" in args:
        create_song_manus_pdf(revue)
    
    elif "signup" in args:
        tex.create_signup_form()
        tex.topdf("rolletilmelding.pdf")



if __name__ == "__main__":

    if "plan" in sys.argv or not os.path.isfile("aktoversigt.plan"):
        sf.create_plan_file("aktoversigt.plan")
        sys.exit("Plan file 'aktoversigt.plan' created successfully.")

    revue = cr.Revue.fromfile("aktoversigt.plan")
    path = revue.conf["Paths"]
    conv = cv.Converter(revue.conf)
    # TODO: Load metadata

    if len(sys.argv) < 2 or "manus" in sys.argv:
        arglist = ("aktoversigt", "roles", "frontpage", "props",
                   "contacts", "material","individual", "songmanus")
    else:
        arglist = sys.argv[1:]

    for arg in arglist:
        create_parts(revue, arg)


    if len(sys.argv) < 2 or "manus" in sys.argv:
        pdf = PDF(revue.conf)
        pdf.pdfmerge((os.path.join(path["pdf"],"forside.pdf"), 
                      os.path.join(path["pdf"],"aktoversigt.pdf"), 
                      os.path.join(path["pdf"],"rolleliste.pdf"), 
                      revue, 
                      os.path.join(path["pdf"],"rekvisitliste.pdf"), 
                      os.path.join(path["pdf"],"kontaktliste.pdf")), 
                      os.path.join(path["pdf"],"manuskript.pdf"))

        print("Manuscript successfully created!")


    # TODO: Save metadata
