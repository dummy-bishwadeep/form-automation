class TemplateConstants:
    task_creation_step_template = {
        "data_col2": ["Step Name", "Display Title", "Description", "Header", "Step Category", "Step Sub Category",
                      "Menu Placement", "Validate Form", "Auto Save", "Sheet"],
        "data_col3": ["<Step Name>", "<Display Title>", "<Description>", "<Header>", "Task Creation Step",
                      "", "Left Navigation", "False", "False", "Step1"],
        "label": "Step1",
        "start_row": 1
    }

    non_periodic_step_template = {
        "data_col2": ["Step Name", "Display Title", "Description", "Header", "Step Category", "Step Sub Category",
                      "Menu Placement", "Validate Form", "Auto Save", "Sheet"],
        "data_col3": ["<Step Name>", "<Display Title>", "<Description>", "<Header>", "Non-Periodic Step",
                      "", "Left Navigation", "False", "False", "Step1"],
        "label": "Step1",
        "start_row": 1
    }

    workflow_metadata_template = {
        "data_col2": ["Workflow Name", "Description", "Categories", "Steps", "Roles"],
        "data_col3": ["<Workflow Name>", "<Description>", "<Categories>", "<Steps Name;except Task Creation Step>", "<Roles>"],
        "label": "Workflow",
        "start_row": 1
    }

    logbook_metadata_template = {
        "data_col2": ["Logbook Name", "Description", "Category", "Business Process Tags", "Card Color", "Workflow",
                      'Task Creation Step', 'Associate Hierarchy'],
        "data_col3": ["<Logbook Name>", "<Description>", "<Categories>", "<Business Process Tags>", "#D8EBFB",
                      "<Workflow Name>", "<Task Creation Step Name>", "Yes"],
        "data_col4": ["", "", "", "", "", "", "", ""],
        "data_col5": ["", "", "", "", "", "", "", ""],
        "label": "Logbook",
        "start_row": 1,
        "hierarchy_level_start_row": 9
    }

    default_step_template = {
        "data_col1": ["<table>", ""],
        "data_col2": ["", "<header>"]
    }