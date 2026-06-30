# # from google import genai

# # client = genai.Client(api_key="YOUR_API_KEY")

# # for model in client.models.list():
# #     print(model.name)

# from firecrawl import Firecrawl

# # firecrawl = Firecrawl(api_key="fc-454f526ae725462baa317891daf052eb")


# # # scrape_status = firecrawl.scrape(
# # #   'https://nahdimandi.com/',
# # #   formats=['markdown', 'html']
# # # )
# # # print(scrape_status)


# # crawl_status = firecrawl.crawl(
# #   'https://nahdimandi.com/',
# #   limit=100,
# #   scrape_options={
# #     'formats': ['markdown', 'html']
# #   }
# # )

# # from docx import Document

# # doc = Document("generated_reports/കാലം കണക്കുതീര്.docx")

# # text = "\n".join(
# #     para.text for para in doc.paragraphs
# # )

# # print(text)
# from tavily import TavilyClient
# import os

# client = TavilyClient(
#     api_key="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"
# )

# query = """
# Tikkaasa Moodal, Kuttippuram — near Markaz
# Famous for authentic tikkas, special tea, fresh juices, and evening snacks. Popular local spot near Markaz with a casual roadside atmosphere.
# """


# def web_search(query: str):
#     response = client.search(query=query, max_results=5)

#     print(response)


# web_search(query)


# res = {
#     "query": "Tikkaasa Moodal, Kuttippuram — near Markaz\nFamous for authentic tikkas, special tea, fresh juices, and evening snacks. Popular local spot near Markaz with a casual roadside atmosphere.",
#     "follow_up_questions": None,
#     "answer": None,
#     "images": [],
#     "results": [
#         {
#             "url": "https://www.justdial.com/Malappuram/Tea-Stalls-in-Kuttippuram/nct-10853304",
#             "title": "Best Tea Stalls in Kuttippuram, Malappuram",
#             "content": "Top Tea Stalls near Kuttippuram, Malappuram. Name, Teatime · Evening Snacks · Irani Tea Stall · Tea Time Cafe · Sakeerka'S Hotel · Hill Top Tea Stall · Arakka",
#             "score": 0.43180037,
#             "raw_content": None,
#         }
#     ],
#     "response_time": 2.41,
#     "request_id": "1ae35011-b32a-4506-9000-d63b05221643",
# }
