* EUCTR publication rates analysis, EU-Trials-Tracker.ebmdatalab.net
* Code by Ben Goldacre, code review Alex Walker. 
* Note: this is pragmatic working code; review alongside paper, SQL and tables. 

*housekeeping
clear all
cd "/Users/bens/Documents/academia/projectsongoing/EUCTR tracker/April 2018 revision"
set more off
capture log using output_for_tables, replace
/*
import excel "/Users/bens/Documents/academia/projectsongoing/EUCTR tracker/April 2018 revision/EUCTR Data_17Jan2018.xlsx", sheet("Final Data") firstrow case(lower)
save bigworking, replace
*/

use bigworking

* labels
rename has_results results
label define noyes 0 "no" 1 "yes"
label values any_terminated noyes
label values all_terminated noyes
label values multiple_sponsors noyes
label values results noyes
label values includes_pip noyes
label define sponsorstatuslabel 0 "noncommercial" 1 "commercial" 2 "mixed/unclear" 3 "blank"
label values sponsor_status sponsorstatuslabel
recode sponsor_status .=3
label define phaselabels 0 "discordant" 1 "1" 2 "2" 3 "3" 4 "4"
label values phase phaselabels
label define rarelabels 0 "no" 1 "yes" 2 "discordant" 3 ”data_not_available”
label values rare rarelabels
label define status 0 "all_ongoing" 1 "all complete (or terminated)" 2 "any complete (or terminated)" 3 "other(suspended)" 4 "blank"
label values trial_status status

* make country count and sponsor count variables
gen country_count=number_of_countries
recode country_count 1=1 2=2 3/99=3
label define counts 1 "1" 2 "2" 3 "3+"
label values country_count counts



* generate "completionyear" variable
gen completionyear=year(max_end_date)
tab completionyear trial_status
drop if completionyear==2000
drop if completionyear==2019
drop if completionyear==2041

* identify trials done by institutions that do a lot of trials
sort sponsor_trial_count
xtile quartile = sponsor_trial_count, nq(4)
xtile decile = sponsor_trial_count, nq(10)
bysort quartile: summ sponsor_trial_count
bysort decile: summ sponsor_trial_count

* make a variable called "bad_sponsor" for unclear sponsor and sponsor not given
gen bad_sponsor=0
replace bad=1 if normalized_name_only=="No Sponsor Name Given"
replace bad=2 if regexm(normalized_name_only,"Unclear Sponsor Name Given")


* note that as with any sponsor name count, the count for "no sponsor name given..." will not match the "sponsor_trial_count" because this is for all sponsors for all trials not just the "max", the sponsor_trial_count will always be equal or higher
label define badsponsorlabel 0 "Fine" 1 "No Sponsor Name Given" 2 "Unclear Sponsor Name Given"
label values bad_sponsor badsponsorlabel

save working, replace

* YOU NOW HAVE A DATASET READY TO DESCRIBE
 
* here are some things that need to run on the full dataset

/*
* Errors, ommissions, inconsistencies
* "While the date for “global end of the trial” is expected to be consistent..."
* create "datedifference" variable denoting discrepancies on completion dates
clear all
use working
gen datedifference=max_end_date-min_end_date
summ datedifference, det
*hist datedifference
gen discrepant_date=datedifference
recode discrepant 0=0 1/max=1
bysort discrepant: summ datediff, det 

* keep only trials where all countries complete
count
keep if trial_status==1
count

* how many are missing a completion date?
count if max_end_date==.
count if max_end_date!=.

*safety net to make sure you now reload data!
clear all

*/

/*
* "Trials with no completion date could not be included ..."
clear all
use working
count
drop if phase==1 & includes_pip==0
count
keep if trial_status==1
count
keep if max_end_date!=.
count
count if max_end_date<=20688
count

clear all
use working
drop if phase==1 & includes_pip==0
count
keep if trial_status==1
count
keep if max_end_date==.
count
tab results

clear all
use working
count
keep if trial_status==2
count
count if max_end_date!=.
tab results

*safety net to make sure you now reload data!
clear all

*/

* Now the tables
clear all
use working

/*if you want to do this for a sensitivity analysis, looking only at trials conducted in one country, then run this first
keep if country_count==1
*/

count

* table 1
tab results, missing
tab completionyear, missing
tab trial_status 
tab phase 
tab sponsor_status
tab includes_pip 
tab rare_disease
tab bioequivalence_study 
tab health_volunteers 
tab quartile
tab bad
tab all_terminated
tab multiple_sponsors
tab country_count

* MAKE "Results Due" STUDY COHORT
count
* keep only trials where all countries complete
keep if trial_status==1
count
* drop if completion date is missing
drop if max_end_date==.
count
* drop if completion date is within past 12 months
display mdy(12, 19, 2016)
drop if max_end_date>20807
count
* drop if phase 1 unless it's a paeds trial
drop if phase==1 & includes_pip==0
tab phase inc
count

save duecohort, replace

* table 1 more
tab results, missing
tab completionyear, missing
tab trial_status 
tab phase 
tab sponsor_status
tab includes_pip 
tab rare_disease
tab bioequivalence_study 
tab health_volunteers 
tab quartile
tab bad
tab all_terminated
tab multiple_sponsors
tab country_count


* table 2 results % 
tab results, missing
proportion results, missing cformat(%5.3f) 

tab completionyear results, missing
proportion results, over(completionyear) missing cformat(%5.3f) 
tab trial_status results
proportion results, over(trial_status) cformat(%5.3f) 
tab phase results
proportion results, over(phase) cformat(%5.3f) 
tab sponsor_status results
proportion results, over(sponsor_status) cformat(%5.3f) 
tab includes_pip results
proportion results, over(includes_pip) cformat(%5.3f) 
tab rare_disease results
proportion results, over(rare_disease) cformat(%5.3f) 
tab bioequivalence_study results 
proportion results, over(bioequivalence) cformat(%5.3f) 
tab health_volunteers results
proportion results, over(health_volunteers) cformat(%5.3f) 
tab quartile results
proportion results, over(quartile) cformat(%5.3f) 
tab bad results
proportion results, over(bad) cformat(%5.3f) 
tab all_terminated results
proportion results, over(all_terminated) cformat(%5.3f) 
tab country_count results
proportion results, over(country_count) cformat(%5.3f) 
tab multiple_sponsors results
proportion results, over(multiple_sponsors) cformat(%5.3f) 



* table 3 logistic regression
*kill v v low data years
drop if completionyear<2005 
*regress!
logistic results completionyear
logistic results ib3.phase
logistic results i.sponsor_status
logistic results i.includes_pip
logistic results i.rare
logistic results i.bioequiv
logistic results i.health
logistic results i.quartile
logistic results i.all_termin
logistic results i.bad
logistic results i.country_count
logistic results i.multiple_sponsors
logistic results completionyear ib3.phase i.sponsor_status i.includes_pip i.rare i.bioequiv i.health i.quartile i.all_termin i.bad i.country_count i.multiple_sponsors, allbaselevels

* Sensitivity analyses requested by editors

* Count of trials as decile
tab decile results
proportion results, over(decile) cformat(%5.3f) 

* Regression using count of trials as continuous variable 
logistic results completionyear sponsor_trial_count ib3.phase i.sponsor_status i.includes_pip i.rare i.bioequiv i.health i.all_termin i.bad i.country_count i.multiple_sponsors, allbaselevels

* Regression with year as dummy variable rather than linear
logistic results ib2016.completionyear ib3.phase i.sponsor_status i.includes_pip i.rare i.bioequiv i.health i.quartile i.all_termin i.bad i.country_count i.multiple_sponsors, allbaselevels

*Regression analysis taking one random trial from each sponsor
clear all
use duecohort
generate random = runiform() 
sort random
bysort name: keep if _n==1
count
logistic results completionyear ib3.phase i.sponsor_status i.includes_pip i.rare i.bioequiv i.health i.quartile i.all_termin i.bad i.country_count i.multiple_sponsors, allbaselevels
