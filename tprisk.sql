create table tp_submission (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,
	client_id INTEGER NOT NULL,
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),
	FOREIGN KEY (client_id) REFERENCES client(id) NOT ENFORCED
)  ORGANIZE BY ROW;

create table tp_user_search_request (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,
	client_id INTEGER NOT NULL,
	user_id varchar(100) NOT NULL,	
	entity_name varchar(100),
	country_code varchar(2),
	street_address varchar(500),
	city varchar(100),
	state varchar(20),
	zip_code varchar(10),	
	ticker varchar(20),	
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),
	FOREIGN KEY (client_id) REFERENCES client(id) NOT ENFORCED
)ORGANIZE BY ROW;


create table tp_request (
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,
	client_id INTEGER NOT NULL,
	submission_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,	
	entity_name varchar(100),
	request_type varchar(100),	
	country_code varchar(2),
	status varchar(100),
	street_address varchar(500),
	city varchar(100),
	state varchar(20),
	zip_code varchar(10),	
	ticker varchar(20),		
	risk_score integer,
	risk_rating char(1),
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),
	FOREIGN KEY (submission_id) REFERENCES tp_submission(id) NOT ENFORCED,
	FOREIGN KEY (client_id) REFERENCES client(id) NOT ENFORCED
)ORGANIZE BY ROW;

create table tp_risk_events(
	id  INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,
	request_id INTEGER,
	analytics varchar(100),
	analytics_id integer,
	risk_event_title varchar(200),
	risk_event_url varchar(200),
	risk_type varchar(10),
	risk_rating char,
	risk_score integer,
	risk_event_date TIMESTAMP NOT NULL DEFAULT now(),	
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),
	false_positive boolean DEFAULT false,
	comments varchar(2000) NULL,
	FOREIGN KEY(analytics_id) REFERENCES ref_analytics(id) NOT ENFORCED,
	FOREIGN KEY (request_id) REFERENCES tp_request(id) NOT ENFORCED
)  ORGANIZE BY ROW;


create table tp_extractor_status(
	request_id integer NOT NULL,
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,	
	source_id varchar(100) NOT NULL,
	source_type varchar(100),
	analytics varchar(100),
	file_name varchar(200),
	status varchar(20),
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),
	PRIMARY KEY (request_id, source_id),
	FOREIGN KEY(request_id) references tp_request(id) NOT ENFORCED,
	FOREIGN KEY(source_id) references ref_extractor_sources(id) NOT ENFORCED
)  ORGANIZE BY ROW;

create table tp_analytics_status(
	request_id integer  NOT NULL,
	encoded_id CHAR(13) FOR BIT DATA NOT NULL UNIQUE,	
	analytics varchar(100),
	analytics_id integer NOT NULL,
	risk_score integer,
	risk_rating char(2),
	status varchar(20),
	first_updated TIMESTAMP NOT NULL DEFAULT now(),
	last_updated TIMESTAMP NOT NULL DEFAULT now(),
	PRIMARY KEY (request_id, analytics_id),
	FOREIGN KEY(request_id) references tp_request(id) NOT ENFORCED,
	FOREIGN KEY(analytics_id) references ref_analytics(id) NOT ENFORCED
)  ORGANIZE BY ROW;

