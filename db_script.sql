CREATE TABLE IF NOT EXISTS public.case_client (
	id serial NOT NULL,
	client_name varchar(100) NULL,
	first_updated timestamp NOT NULL DEFAULT now(),
	last_updated timestamp NOT NULL DEFAULT now(),
	CONSTRAINT case_client_pkey PRIMARY KEY (id),
	CONSTRAINT case_unique_constraint UNIQUE (client_name)
);
CREATE TABLE IF NOT EXISTS public.case_client_engagement (
	id serial NOT NULL,
	client_id int4 NULL,
	engagement_name varchar(150) NULL,
	first_updated timestamp NOT NULL DEFAULT now(),
	last_updated timestamp NOT NULL DEFAULT now(),
	reporting_hierarchy varchar(500) NULL,
	CONSTRAINT case_client_engagement_pkey PRIMARY KEY (id),
	CONSTRAINT case_eng_constraint UNIQUE (client_id,engagement_name)
);
CREATE TABLE IF NOT EXISTS public.case_contracts (
	id serial NOT NULL,
	client_id int4 NULL,
	engagement_id int4 NULL,
	contract_name varchar(300) NULL,
	contract_type varchar(100) NULL,
	status varchar(150) NULL,
	first_updated timestamp NOT NULL DEFAULT now(),
	last_updated timestamp NOT NULL DEFAULT now(),
	effective_date date NULL,
	graph_id int4 NULL,
	parent_id int4 NULL,
	"location" varchar(300) NULL,
	job_id varchar(200) NULL,
	effective_start_date varchar(100) NULL,
	effective_end_date varchar(100) NULL,
	CONSTRAINT case_contracts_client_id_engagement_id_contract_name_key UNIQUE (client_id, engagement_id, contract_name),
	CONSTRAINT case_contracts_pkey PRIMARY KEY (id),
	CONSTRAINT case_contracts_client_id_fkey FOREIGN KEY (client_id) REFERENCES case_client(id),
	CONSTRAINT case_contracts_engagement_id_fkey FOREIGN KEY (engagement_id) REFERENCES case_client_engagement(id)
);
CREATE TABLE IF NOT EXISTS public.case_contracts_approvers (
	id serial NOT NULL,
	"name" varchar(150) NULL,
	title varchar(150) NULL,
	approved_date varchar(150) NULL,
	first_updated timestamp NOT NULL DEFAULT now(),
	last_updated timestamp NOT NULL DEFAULT now(),
	CONSTRAINT case_contracts_approvers_pkey PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS public.case_ref_table_definition (
	id serial NOT NULL,
	"name" varchar(200) NULL,
	description varchar(200) NULL,
	table_pattern varchar(200) NULL,
	CONSTRAINT case_ref_table_definition_pkey PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS public.case_contracts_items (
	id serial NOT NULL,
	contract_id int4 NULL,
	"location" varchar(300) NULL,
	status varchar(150) NULL,
	ref_table_id int4 NULL,
	first_updated timestamp NOT NULL DEFAULT now(),
	last_updated timestamp NOT NULL DEFAULT now(),
	content_type varchar(50) NULL,
	table_type varchar(30) NULL,
	CONSTRAINT case_contracts_items_pkey PRIMARY KEY (id),
	CONSTRAINT case_contracts_items_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES case_contracts(id),
	CONSTRAINT case_contracts_items_ref_table_id_fkey FOREIGN KEY (ref_table_id) REFERENCES case_ref_table_definition(id)
);
CREATE TABLE IF NOT EXISTS public.case_contracts_properties (
	id serial NOT NULL,
	contract_id int4 NULL,
	"key" varchar(150) NULL,
	value varchar(150) NULL,
	first_updated timestamp NOT NULL DEFAULT now(),
	last_updated timestamp NOT NULL DEFAULT now(),
	CONSTRAINT case_contracts_properties_pkey PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS public.case_error_table (
	id serial NOT NULL,
	contract_id int4 NULL,
	reason varchar(300) NULL,
	CONSTRAINT case_error_table_pkey PRIMARY KEY (id),
	CONSTRAINT case_error_table_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES case_contracts(id)
);
CREATE TABLE IF NOT EXISTS public.case_ref_contract_types (
	id serial NOT NULL,
	contract_type varchar(100) NOT NULL,
	CONSTRAINT case_ref_contract_types_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.case_ref_table_category (
	id serial NOT NULL,
	table_type varchar(150) NOT NULL,
	keywords varchar(200) NOT NULL,
	CONSTRAINT case_ref_table_category_pkey PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS public.case_ref_table_sla_rules (
	id serial NOT NULL,
	table_id int4 NULL,
	title varchar(100) NULL,
	qualifier_1 varchar(100) NULL,
	qualifier_2 varchar(100) NULL,
	CONSTRAINT case_ref_table_sla_rules_pkey PRIMARY KEY (id),
	CONSTRAINT case_ref_table_sla_rules_table_id_fkey FOREIGN KEY (table_id) REFERENCES case_ref_table_definition(id)
);
CREATE TABLE IF NOT EXISTS public.case_ref_table_schedule_rules (
	id serial NOT NULL,
	sla_id int4 NULL,
	minimum varchar(100) NULL,
	target varchar(100) NULL,
	start_date varchar(100) NULL,
	end_date varchar(100) NULL,
	calculation varchar(100) NULL,
	CONSTRAINT case_ref_table_schedule_rules_pkey PRIMARY KEY (id),
	CONSTRAINT case_ref_table_schedule_rules_sla_id_fkey FOREIGN KEY (sla_id) REFERENCES case_ref_table_sla_rules(id)
);

CREATE TABLE IF NOT EXISTS public.case_users (
	id serial NOT NULL,
	client_id int4 NULL,
	user_name varchar(100) NOT NULL,
	first_name varchar(100) NULL,
	last_name varchar(100) NULL,
	email varchar(100) NOT NULL,
	"password" varchar(100) NULL,
	CONSTRAINT case_users_email_key UNIQUE (email),
	CONSTRAINT case_users_pkey PRIMARY KEY (id),
	CONSTRAINT case_users_user_name_key UNIQUE (user_name)
);
CREATE TABLE IF NOT EXISTS public."document" (
	client_id varchar(150) NOT NULL,
	document_id varchar(150) NOT NULL,
	project varchar(15) NOT NULL,
	status varchar(50) NULL,
	pub_date timestamp NULL,
	updated_date timestamp NULL,
	id serial NOT NULL,
	CONSTRAINT document_pkey PRIMARY KEY (id)
);
COMMIT;

INSERT INTO public.case_ref_contract_types VALUES (1, 'MSA');
INSERT INTO public.case_ref_contract_types VALUES (2, 'MSA Amendment');
INSERT INTO public.case_ref_contract_types VALUES (3, 'SOW');
INSERT INTO public.case_ref_contract_types VALUES (4, 'SOW Amendment');

INSERT INTO public.case_ref_table_category VALUES (1, 'RU', '$,USD,Pricing,Unit Price,£,GBP,€,EURO,¥,YEN');
INSERT INTO public.case_ref_table_category VALUES (2, 'SLA', 'Service Level,Monthly Service Levels,Availability,Uptime,%,Performance Indicators,Performance Indicator,Performance measurement,CPI,KPI');

COMMIT;

CREATE OR REPLACE FUNCTION public.updateEffectiveDate(conid integer)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
  parentid integer; 
  startDate varchar;
  endDate varchar;
  approvedStartDate varchar;
  approvedDate date:= null;
BEGIN
	
	FOR approvedStartDate IN select approved_date from case_contracts_approvers
								where approved_date != '' and id in (select CAST (value AS INTEGER) from case_contracts_properties 
								where contract_id= conid  and  "key" = 'approverId' 
								and exists(select 1 from case_contracts_properties where  "key" ='effectiveStartDateUponSign' )) loop
	BEGIN
		if ( approvedDate < to_date(approvedStartDate,'MM/DD/YYYY') or approvedDate is null) then 
			approvedDate := to_date(approvedStartDate, 'MM/DD/YYYY');
		end if;
	
	EXCEPTION
	WHEN OTHERS  THEN
	  CONTINUE;
	END;
	END LOOP;	
	
	    if (approvedDate is not null) then
	        startDate := TO_CHAR(approvedDate, 'MM/DD/YYYY');
	    else 
	    	select max(value) into startDate from case_contracts_properties where contract_id= conid and key='effectiveStartDate';
	    end if;
    
		select max(value) into endDate from case_contracts_properties where contract_id= conid and key='effectiveEndDate';
    
	    if (startDate is null and endDate is null) then
	    	select CAST (parent_id AS INTEGER) into parentid from case_contracts where id = conid;
			select CAST (effective_start_date AS varchar) into startDate from case_contracts where id = parentid;
			select CAST (effective_end_date AS varchar) into endDate from case_contracts where id = parentid;
	    end if;
	    
	    
     	if (startDate is null and parentid is not null) then
	    	LOOP 
		     EXIT WHEN parentid is not null;
		      select max(value) into startDate from case_contracts_properties where contract_id= parentid and key='effectiveStartDate';
				if (startDate is not null ) then
					parentid := null;
				else 
					select parent_id into parentid from case_contracts where id = parent_id;
				end if;
	   		END LOOP ;
	    end if;
		if (endDate is null and parentid is not null) then
	    	LOOP 
		     EXIT WHEN parentid is null;
				select max(value) into endDate from case_contracts_properties where contract_id= parentid and key='effectiveEndDate';
				if (endDate is not null ) then
					parentid := null;
				else 
					select parent_id into parentid from case_contracts where id = parent_id;
				end if;
	   		END LOOP ;
	    end if;
		
	    	if (startDate is not null ) then
      			update case_contracts set effective_start_date = startDate 
      		 	where id=conid;
	        end if;
	        if (endDate is not null ) then
      			update case_contracts set effective_end_date = endDate 
      		 	where id=conid;
	        end if; 
	        
	        return conid;
END;
$$ ;
