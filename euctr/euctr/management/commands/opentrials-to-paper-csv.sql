CREATE TEMP TABLE PSpons1 ON COMMIT DROP AS
SELECT
    eudract_number,
    eudract_number_with_country,
    s -> 'name_of_sponsor' AS name_of_sponsor,
    s -> 'status_of_the_sponsor' AS status_of_sponsor
FROM
    euctr,
    jsonb_array_elements (euctr.sponsors) AS s;

CREATE TEMP TABLE PSpons2 AS
SELECT
    eudract_number,
    count (*) AS Total,
    max (CAST (name_of_sponsor AS text)) AS name_of_sponsor_arb,
    count ( CASE
            WHEN status_of_sponsor = '"Non-Commercial"' THEN 1
            ELSE NULL
        END) AS status_of_sponsor_NC,
    count ( CASE
            WHEN status_of_sponsor = '"Commercial"' THEN 1
            ELSE NULL
        END) AS status_of_sponsor_C,
    count ( CASE
            WHEN CAST (status_of_sponsor AS text)
            IS NULL
            OR CAST (status_of_sponsor AS text)
            = '' THEN 1
            ELSE NULL
        END) AS status_of_sponsor_Blank
FROM
    PSpons1
GROUP BY
    eudract_number;

CREATE TEMP TABLE PSpons3 AS
SELECT
    eudract_number AS Trial_ID,
    CASE
        WHEN status_of_sponsor_NC = Total THEN 0
        WHEN status_of_sponsor_C = Total THEN 1
        WHEN status_of_sponsor_Blank = Total THEN 3
        ELSE 2
    END AS Sponsor_Status,
    name_of_sponsor_arb
FROM
    PSpons2;

CREATE TEMP TABLE PTemp1 AS
SELECT
    eudract_number,
    count (*) AS Total,
    count ( CASE
            WHEN end_of_trial_status = 'Completed' THEN 1
            ELSE NULL
        END) AS completed,
    count ( CASE
            WHEN end_of_trial_status = 'Ongoing'
            OR end_of_trial_status = 'Restarted' THEN 1
            ELSE NULL
        END) AS ongoing,
    count ( CASE
            WHEN end_of_trial_status = 'Suspended by CA'
            OR end_of_trial_status = 'Temporarily Halted' THEN 1
            ELSE NULL
        END) AS suspended,
    count ( CASE
            WHEN end_of_trial_status = 'Prematurely Ended' THEN 1
            ELSE NULL
        END) AS terminated,
    count ( CASE
            WHEN end_of_trial_status = 'Withdrawn' THEN 1
            ELSE NULL
        END) AS withdrawn,
    count ( CASE
            WHEN end_of_trial_status = 'Not Authorised'
            OR end_of_trial_status = 'Prohibited by CA' THEN 1
            ELSE NULL
        END) AS other,
    count ( CASE
            WHEN end_of_trial_status IS NULL THEN 1
            ELSE NULL
        END) AS empty,
    count ( CASE
            WHEN trial_results IS NOT NULL
            OR trial_results <> '' THEN 1
            ELSE NULL
        END) AS results,
    count ( CASE
            WHEN date_of_the_global_end_of_the_trial IS NOT NULL THEN 1
            ELSE NULL
        END) AS comp_date,
    count (DISTINCT date_of_the_global_end_of_the_trial) AS distinct_comp_date,
    max (date_of_the_global_end_of_the_trial) AS max_end_date,
    min (date_of_the_global_end_of_the_trial) AS min_end_date,
    count ( CASE
            WHEN CAST (trial_is_part_of_a_paediatric_investigation_plan AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS Includes_PIP,
    count ( CASE
            WHEN trial_condition_being_studied_is_a_rare_disease = 'No' THEN 1
            ELSE NULL
        END) AS Rare_Disease_No,
    count ( CASE
            WHEN trial_condition_being_studied_is_a_rare_disease = 'Yes' THEN 1
            ELSE NULL
        END) AS Rare_Disease_Yes,
    count ( CASE
            WHEN trial_condition_being_studied_is_a_rare_disease = 'Information not present in EudraCT' THEN 1
            ELSE NULL
        END) AS Rare_Disease_Empty,
    count ( CASE
            WHEN CAST (trial_therapeutic_use_phase_iv AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS phase_iv_trial,
    count ( CASE
            WHEN CAST (trial_therapeutic_use_phase_iv AS text)
            LIKE 'f%' THEN 1
            ELSE NULL
        END) AS not_phase_iv_trial,
    count ( CASE
            WHEN CAST (trial_therapeutic_confirmatory_phase_iii AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS phase_iii_trial,
    count ( CASE
            WHEN CAST (trial_therapeutic_confirmatory_phase_iii AS text)
            LIKE 'f%' THEN 1
            ELSE NULL
        END) AS not_phase_iii_trial,
    count ( CASE
            WHEN CAST (trial_therapeutic_exploratory_phase_ii AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS phase_ii_trial,
    count ( CASE
            WHEN CAST (trial_therapeutic_exploratory_phase_ii AS text)
            LIKE 'f%' THEN 1
            ELSE NULL
        END) AS not_phase_ii_trial,
    count ( CASE
            WHEN CAST (trial_human_pharmacology_phase_i AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS phase_i_trial,
    count ( CASE
            WHEN CAST (trial_human_pharmacology_phase_i AS text)
            LIKE 'f%' THEN 1
            ELSE NULL
        END) AS not_phase_i_trial,
    count ( CASE
            WHEN CAST (trial_bioequivalence_study AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS bioequivalence_study_yes,
    count ( CASE
            WHEN CAST (trial_bioequivalence_study AS text)
            LIKE 'f%' THEN 1
            ELSE NULL
        END) AS bioequivalence_study_no,
    count ( CASE
            WHEN CAST (subject_healthy_volunteers AS text)
            LIKE 't%' THEN 1
            ELSE NULL
        END) AS healthy_volunteers_yes,
    count ( CASE
            WHEN CAST (subject_healthy_volunteers AS text)
            LIKE 'f%' THEN 1
            ELSE NULL
        END) AS healthy_volunteers_no
FROM
    euctr
GROUP BY
    eudract_number;

SELECT
    eudract_number AS Trial_ID,
    Total AS Number_of_Countries,
    min_end_date,
    max_end_date,
    comp_date,
    CASE
        WHEN results = 0 THEN 0
        ELSE 1
    END AS has_results,
    CASE
        WHEN Includes_PIP > 0 THEN 1
        ELSE 0
    END AS Includes_PIP,
    CASE
        WHEN Rare_Disease_No = Total THEN 0
        WHEN Rare_Disease_Yes = Total THEN 1
        WHEN Rare_Disease_Empty = Total THEN 3
        ELSE 2
    END AS Rare_Disease,
    CASE
        WHEN phase_i_trial = Total THEN 1
        WHEN phase_ii_trial = Total THEN 2
        WHEN phase_iii_trial = Total THEN 3
        WHEN phase_iv_trial = Total THEN 4
        ELSE 0
    END AS Phase,
    CASE
        WHEN bioequivalence_study_no = Total THEN 0
        WHEN bioequivalence_study_yes = Total THEN 1
        ELSE 2
    END AS bioequivalence_study,
    CASE
        WHEN healthy_volunteers_no = Total THEN 0
        WHEN healthy_volunteers_yes = Total THEN 1
        ELSE 2
    END AS health_volunteers,
    CASE
        WHEN ongoing = Total THEN 0
        WHEN completed + terminated = Total THEN 1
        WHEN ((completed + terminated)
            > 0
            AND (completed + terminated)
            < total)
        THEN 2
        WHEN empty = total THEN 4
        ELSE 3
    END AS Trial_status,
    CASE
        WHEN terminated > 0 THEN 1
        ELSE 0
    END AS terminated,
    PSpons3.Sponsor_Status,
    trim (BOTH '"'
        FROM
        PSpons3.name_of_sponsor_arb) AS name_of_sponsor
FROM
    PTemp1
    LEFT JOIN PSpons3 ON PTemp1.eudract_number = PSpons3.Trial_ID;
