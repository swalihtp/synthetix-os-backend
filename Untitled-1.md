
**Root Path:** `c:\Users\DELL\Desktop\SYNTHETIX OS\synthetix-os-backend`

synthetix-os-backend
├── .agents
├── .pytest_cache
│   ├── v
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── README.md
├── accounts
│   ├── management
│   │   └── commands
│   │       └── seed_rbac.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_emailverification.py
│   │   └── __init__.py
│   ├── permissions
│   │   └── rbac_permission.py
│   ├── serializers
│   │   ├── changepassword_serializer.py
│   │   ├── forgotpassword_serializer.py
│   │   ├── login_serializer.py
│   │   ├── register_serializer.py
│   │   ├── resetpassword_serializer.py
│   │   ├── update_profile_serializer.py
│   │   ├── user_serializer.py
│   │   └── verify_email_serializer.py
│   ├── services
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   ├── google_auth_service.py
│   │   ├── mfa_service.py
│   │   └── rbac_service.py
│   ├── tests
│   │   ├── conftest.py
│   │   ├── test_google_login.py
│   │   ├── test_login.py
│   │   ├── test_logout.py
│   │   ├── test_mfa.py
│   │   ├── test_password.py
│   │   ├── test_profile.py
│   │   ├── test_register.py
│   │   └── test_verifications.py
│   ├── utils
│   │   ├── otp_geneation.py
│   │   └── password_reset_token.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── throttles.py
│   ├── urls.py
│   └── views.py
├── agent
│   ├── management
│   │   ├── commands
│   │   │   ├── __init__.py
│   │   │   └── seed_templates.py
│   │   └── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_agent_unique_agent_per_user.py
│   │   ├── 0003_agent_agent_schema_builtinagent_input_schema.py
│   │   ├── 0004_agentdocuments.py
│   │   ├── 0005_s3marketintelligencereport.py
│   │   ├── 0006_agentexecution.py
│   │   ├── 0007_alter_agentexecution_id.py
│   │   ├── 0008_agentexecution_scraped_data_from_competitor_websites_and_more.py
│   │   ├── 0009_builtinagent_required_integrations.py
│   │   ├── 0010_builtinagent_capabilities_builtinagent_tools.py
│   │   ├── 0011_agentdocuments_created_at_and_more.py
│   │   └── __init__.py
│   ├── tests
│   │   ├── conftest.py
│   │   ├── test_agent_views.py
│   │   └── test_builtin_agent_views.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── pagination.py
│   ├── routing.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── urls.py
│   └── views.py
├── ai_service
│   ├── api
│   │   ├── __init__.py
│   │   ├── analyze_intentions.py
│   │   ├── documents.py
│   │   ├── email_agent.py
│   │   ├── execute.py
│   │   ├── market_agent.py
│   │   ├── meeting_notes.py
│   │   ├── resume_analysis.py
│   │   ├── store_doc.py
│   │   └── summarization.py
│   ├── schemas
│   │   ├── company_profile.py
│   │   ├── competitor.py
│   │   ├── request.py
│   │   ├── response.py
│   │   └── swot.py
│   ├── services
│   │   ├── email_agent
│   │   │   ├── llm.py
│   │   │   ├── prompt.py
│   │   │   ├── retreiver.py
│   │   │   ├── schemas.py
│   │   │   └── tools.py
│   │   ├── market_agent
│   │   │   ├── llm.py
│   │   │   ├── prompt.py
│   │   │   └── schemas.py
│   │   ├── env.py
│   │   └── llm_service.py
│   ├── tasks
│   │   ├── company_profile.py
│   │   ├── competitor_analysis.py
│   │   ├── competitor_discovery.py
│   │   ├── executive_summary.py
│   │   ├── market_report.py
│   │   ├── market_trends.py
│   │   ├── profile_enrichment.py
│   │   ├── recommendations.py
│   │   ├── research_gap.py
│   │   └── swot.py
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   ├── temp.txt
│   └── test_llm.py
├── dashboard
│   ├── migrations
│   │   └── __init__.py
│   ├── tests
│   │   ├── conftest.py
│   │   └── test_dashboard_view.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── selectors.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── integrations
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_processedemail_user.py
│   │   └── __init__.py
│   ├── services
│   │   ├── extractors
│   │   │   ├── base.py
│   │   │   ├── nextjs_extractor.py
│   │   │   ├── playwright_extractor.py
│   │   │   ├── requests_extractor.py
│   │   │   └── wordpress_extractor.py
│   │   ├── parsers
│   │   │   ├── base_parser.py
│   │   │   ├── blog_parser.py
│   │   │   ├── e_commerse_parser.py
│   │   │   ├── generic_parser.py
│   │   │   └── news_parser.py
│   │   ├── content_parser.py
│   │   ├── extraction_engine.py
│   │   ├── market_intelligence_pipeline.py
│   │   ├── scraping_strategy_planner.py
│   │   └── website_intelligence.py
│   ├── tests
│   │   ├── conftest.py
│   │   └── test_integrations.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── gmail.py
│   ├── gmail_watch.py
│   ├── models.py
│   ├── serializers.py
│   ├── telegram.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── persona
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── tests
│   │   ├── conftest.py
│   │   └── test_persona_views.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── requirements
│   ├── core.txt
│   ├── dev.txt
│   ├── integrations.txt
│   └── ml.txt
├── review
├── static
├── synthetix_os
│   ├── settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── system_admin
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── serializers
│   │   ├── admin_register_serializer.py
│   │   ├── dashboard_statistics_serializer.py
│   │   ├── email_activity_stream.py
│   │   └── user_registry_serializer.py
│   ├── services
│   │   ├── accept_invitation_service.py
│   │   ├── admin_services.py
│   │   ├── create_admin_service.py
│   │   └── dashboard_statistics_service.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_system_admin_views.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── pagination.py
│   ├── permission.py
│   ├── throttles.py
│   ├── urls.py
│   └── views.py
├── triggers
│   ├── migrations
│   │   └── __init__.py
│   ├── tests
│   │   ├── conftest.py
│   │   └── test_gmail_webhook.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── email_urls.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── workflows
│   ├── email_workflow
│   │   ├── nodes
│   │   │   ├── ai.py
│   │   │   ├── analyze_intent.py
│   │   │   ├── create_email_execution.py
│   │   │   ├── deduplicate.py
│   │   │   ├── document_processing.py
│   │   │   ├── extract_attachments.py
│   │   │   ├── fetch_email.py
│   │   │   ├── human_review.py
│   │   │   ├── initialize.py
│   │   │   └── reply.py
│   │   ├── routers
│   │   │   ├── decide_process_after_intent_analysis.py
│   │   │   ├── decide_process_router.py
│   │   │   ├── decide_to_human_review.py
│   │   │   ├── decision_router.py
│   │   │   └── should_continue.py
│   │   ├── services
│   │   │   ├── ai
│   │   │   │   └── ai_service.py
│   │   │   ├── documents
│   │   │   │   ├── extractors
│   │   │   │   │   ├── csv_extractor.py
│   │   │   │   │   ├── docx_extractor.py
│   │   │   │   │   ├── image_extractor.py
│   │   │   │   │   ├── pdf_extractor.py
│   │   │   │   │   ├── txt_extractor.py
│   │   │   │   │   └── xlsx_extractor.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── cleaner.py
│   │   │   │   │   ├── downloader.py
│   │   │   │   │   └── mime.py
│   │   │   │   ├── exceptions.py
│   │   │   │   └── processer.py
│   │   │   ├── other
│   │   │   └── s3_upload.py
│   │   ├── graph.py
│   │   └── state.py
│   ├── gmail_notification
│   │   ├── nodes
│   │   │   ├── deduplicate_pubsub_node.py
│   │   │   ├── enqueue_email_jobs_node.py
│   │   │   ├── fetch_history_changes_node.py
│   │   │   ├── resolve_user_node.py
│   │   │   ├── should_continue_node.py
│   │   │   └── validate_payload_node.py
│   │   ├── graph.py
│   │   └── state.py
│   ├── market_inteligence_workflow
│   │   ├── node
│   │   │   ├── additional_research.py
│   │   │   ├── company_profiling.py
│   │   │   ├── competitor_discovery.py
│   │   │   ├── competitor_research.py
│   │   │   ├── crawl_company_website.py
│   │   │   ├── executive_summary_generation.py
│   │   │   ├── load_documents.py
│   │   │   ├── market_trend_analysis.py
│   │   │   ├── recommendation_generation.py
│   │   │   ├── report_generation.py
│   │   │   ├── research_gap_detection.py
│   │   │   ├── send_report.py
│   │   │   ├── swot_generation.py
│   │   │   └── upload_to_s3.py
│   │   ├── routers
│   │   │   ├── decide_process_router.py
│   │   │   ├── decide_process_router2.py
│   │   │   └── route_gap_research.py
│   │   ├── services
│   │   │   ├── ai_services
│   │   │   │   └── ai_service.py
│   │   │   ├── tools
│   │   │   │   ├── generate_pdf.py
│   │   │   │   └── web_search.py
│   │   │   ├── ai_client.py
│   │   │   ├── ai_service.py
│   │   │   ├── document_service.py
│   │   │   ├── firecrawsl_service.py
│   │   │   └── tavily_service.py
│   │   ├── utils
│   │   │   └── text_chunker.py
│   │   ├── graph.py
│   │   ├── new_graph.py
│   │   ├── prompt.py
│   │   └── state.py
│   ├── meeting_notes_generator_workflow
│   │   ├── nodes
│   │   │   ├── action_item_extraction_node.py
│   │   │   ├── decision_extraction_node.py
│   │   │   ├── extract_text_node.py
│   │   │   ├── generate_meeting_summary_node.py
│   │   │   ├── initialize_node.py
│   │   │   ├── store_summary_node.py
│   │   │   └── topic_detection_node.py
│   │   ├── routers
│   │   │   └── can_extract_router.py
│   │   ├── services
│   │   │   ├── ai
│   │   │   │   ├── __init__.py
│   │   │   │   └── ai_service.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── state.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_workflowforhumanreview_email_body.py
│   │   ├── 0003_workflowforhumanreview_agent_id.py
│   │   ├── 0004_remove_workflowforhumanreview_agent_id_and_more.py
│   │   ├── 0005_workflowforhumanreview_agent_and_more.py
│   │   ├── 0006_alter_workflowforhumanreview_human_choice.py
│   │   ├── 0007_alter_workflowforhumanreview_options_and_more.py
│   │   ├── 0008_workflowexecution.py
│   │   ├── 0009_alter_workflowforhumanreview_options.py
│   │   ├── 0010_emailexecutionresult.py
│   │   ├── 0011_emailexecution.py
│   │   ├── 0012_alter_emailexecution_email_id_and_more.py
│   │   ├── 0013_dailyaiusagesnapshot_aiusagelog.py
│   │   ├── 0014_resumeexecution.py
│   │   ├── 0015_meetingsummaryexecution.py
│   │   ├── 0016_meetingsummaryexecution_summary_style.py
│   │   ├── 0017_alter_resumeexecution_file_name_and_more.py
│   │   ├── 0018_resumeexecution_retry_fields.py
│   │   └── __init__.py
│   ├── resume_analyzer_workflow
│   │   ├── nodes
│   │   │   ├── ats_scoring_node.py
│   │   │   ├── create_email_execution_node.py
│   │   │   ├── extract_text_node.py
│   │   │   ├── generate_feedback_node.py
│   │   │   ├── initialize_node.py
│   │   │   ├── resume_analysis_node.py
│   │   │   ├── skill_evaluation_node.py
│   │   │   └── store_analysis_node.py
│   │   ├── routers
│   │   │   └── can_extract_router.py
│   │   ├── services
│   │   │   ├── ai
│   │   │   │   ├── __init__.py
│   │   │   │   └── ai_service.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── state.py
│   ├── services
│   │   └── workflow_builder.py
│   ├── tests
│   │   ├── conftest.py
│   │   ├── test_storage_backed_extraction.py
│   │   ├── test_workflow_additional_views.py
│   │   └── test_workflow_views.py
│   ├── utils
│   │   ├── realtime.py
│   │   └── storage.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── pagination.py
│   ├── scheduler.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
├── manage.py
├── projection.npy
├── pytest.ini
├── test.py
└── test_ai_generation.py
