<h1 align="center">📊 Result Sheet Analyzer (Electrical Engineering)</h1><br>



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

## Key Features

>01. Accepts multiple PDF result sheets

>02. Automatically detects subject code and name
(Format: CODE – Subject Name, e.g., MA1023 – Engineering Mathematics)

>03. Extracts index numbers and final grades from tables

>04. Calculates GPA using predefined grade points

>05. Supports different credit values per subject

>06. Filters only common index numbers
(Students who appear in all subject PDFs — excluding other departments)

>07. Generates a single consolidated Excel sheet

>08. Credit values are fully configurable
