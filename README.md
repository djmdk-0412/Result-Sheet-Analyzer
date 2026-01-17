<h1 align="center">📊  University Result Sheet Analyzer (Electrical Engineering)</h1><br>



## Project Overview


  The Result Sheet Analyzer is a Python-based academic automation tool designed specifically for the Electrical Engineering Department.It processes multiple PDF result sheets (one per subject/module) and generates a single consolidated result sheet containing subject grades and the final GPA for each eligible student.

  
This project aims to reduce manual effort, eliminate human errors, and provide a reliable way to analyze departmental examination results.

## Problem Statement

In university examination systems:

> **Each subject releases results separately as PDF files**

> **PDFs often include students from multiple departments**

> **Subjects have different credit values**

> **Manual consolidation of results is time-consuming and error-prone**

This tool automates the entire process while ensuring accuracy and department-level filtering.



A Python-based automation tool that extracts, repairs, merges, and analyzes university examination result PDFs to generate a **clean consolidated result sheet with GPA calculation**.

This project is specially designed to handle **broken PDF encodings** where student index numbers appear missing or invisible.

---

##  Key Features

- ✅ Extracts student **Index Numbers and Grades** from result PDFs  
- ✅ Repairs **Shift-29 / invisible digit encoding issues** in PDFs  
- ✅ Merges results from **multiple subjects**
- ✅ Attaches **student names** from a CSV / Excel database
- ✅ Calculates **GPA** using subject credit weights
- ✅ Outputs a **final structured result sheet** using Pandas

---


