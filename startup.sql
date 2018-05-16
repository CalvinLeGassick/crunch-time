CREATE TABLE COMPANY (
    -- Comes with /organizations
    company_uuid char(32) PRIMARY KEY,
    company_name TEXT NOT NULL,
    short_description TEXT NOT NULL,
    company_url TEXT,
    company_permalink TEXT NOT NULL UNIQUE,
    company_crunchbase_creation date NOT NULL
    company_city TEXT,
    company_region TEXT,
    company_country TEXT
    -- web_path TEXT,
    -- api_path TEXT

    -- Comes from detail view
    -- company_min_employees INTEGER,
    -- company_max_employees INTEGER,
    -- company_is_closed BOOLEAN,
    -- company_closed_on DATE,
    -- company_total_funding_usd INTEGER
);
CREATE TABLE CATEGORY (
    category_uuid char(32) PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);
CREATE TABLE COMPANY_CATEGORY (
    company_uuid char(32) REFERENCES company,
    category_uuid char(32) REFERENCES category,
    PRIMARY KEY (company_uuid, category_uuid)
);
