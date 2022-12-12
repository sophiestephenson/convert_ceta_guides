# convert_ceta_guides

Script to download a list of CETA guides as docx, then convert to md. 
After making sure the md is accurate, we will put the .md guides on
our [website](techclinic.cs.wisc.edu) and attribute CETA.

To use:
- Download the [CETA guides dashboard](https://docs.google.com/spreadsheets/d/1JShWdURTLQAihi0cxaqo0stImRs14YQOp6j8fecrEbs/edit#gid=0) as `ceta_dashboard.csv`.
- Run `python3 convert_guides.py`.
- Manually check the guides - pandoc doesn't 100% capture everything in the docs.

Note: I have manually added links to newer guides that are not on the above spreadsheet. Those might go out of date.