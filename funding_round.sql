CREATE TABLE FUNDING_ROUND (
    funding_uuid char(32) PRIMARY KEY,
    company_uuid char(32) REFERENCES company,
    funding_round_type TEXT,
    series char(1),
    announced_on DATE,
    announced_on_trust_code INTEGER CHECK (announced_on_trust_code >= 0 AND announced_on_trust_code <= 7),
    closed_on DATE,
    closed_on_trust_code INTEGER CHECK (closed_on_trust_code >= 0 AND closed_on_trust_code <= 7),
    money_raised_usd INTEGER,
    target_money_raised_usd INTEGER,
    created_at DATE
);

-- SELECT EXTRACT(YEAR FROM announced_on) as year, SUM(money_raised_usd)
-- FROM funding_round
-- GROUP BY year
-- ORDER BY year;
