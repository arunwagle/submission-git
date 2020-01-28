create table everestschema.evre_learning_email_msgs (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),	
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,
	business_segment_id INTEGER NOT NULL,
	status varchar(100),
	document_name varchar(500) NOT NULL,
	USED_FOR VARCHAR(20),
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now()
)  ORGANIZE BY ROW;

create table everestschema.evre_learning_email_attachments (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
	evre_email_msg_id INTEGER,
	evre_email_msg_encoded_id CHAR(13), 
	document_name varchar(500) NOT NULL,
	document_type varchar(50) NOT NULL,
	classification_type varchar(50),
	status varchar(100),
	USED_FOR VARCHAR(20),
	DESCRIPTION VARCHAR(50),
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),	
	FOREIGN KEY (evre_email_msg_id) REFERENCES everestschema.evre_learning_email_msgs(id) NOT ENFORCED
)  ORGANIZE BY ROW;

create table everestschema.evre_learning_split_content (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
	evre_email_msg_id INTEGER,
	evre_learning_email_attachments_id INTEGER,
	document_name varchar(500) NOT NULL,
	document_type varchar(50) NOT NULL,
	classification_type varchar(50),
	status varchar(100),
	USED_FOR VARCHAR(20),
	DESCRIPTION VARCHAR(50),
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),	
	FOREIGN KEY (evre_email_msg_id) REFERENCES everestschema.evre_learning_email_msgs(id) NOT ENFORCED,
	FOREIGN KEY (evre_learning_email_attachments_id) REFERENCES everestschema.evre_learning_email_attachments(id) NOT ENFORCED
)  ORGANIZE BY ROW;


create table everestschema.evre_learning_error_table (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),	
	evre_email_msg_id INTEGER,
	reason varchar(300) NULL
)  ORGANIZE BY ROW;





