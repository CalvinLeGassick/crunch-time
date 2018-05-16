COPY (
    SELECT DISTINCT company_name, 'https://www.crunchbase.com/' || LOWER(company_web_path) AS crunch_url
    FROM company
    JOIN company_category ON company.company_uuid=company_category.company_uuid
    JOIN category ON company_category.category_uuid=category.category_uuid
    WHERE
    category.category_name
    IN (
        'Artificial Intelligence',
        'Autonomous Vehicles',
        'Machine Learning',
        'Natural Language Processing',
        'Computer Vision',
        'Facial Recognition',
        'Image Recognition',
        'Speech Recognition',
        'Semantic Search',
        'Semantic Web',
        'Text Analytics',
        'Virtual Assistant',
        'Visual Search',
        'Predictive Analytics',
        'Intelligent Systems'
        )
    ORDER BY company_name
    )
TO '~/company_list.csv' (format CSV);