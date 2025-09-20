from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Prompt for document analysis
document_analysis_prompt = ChatPromptTemplate.from_template("""
You are a financial analyst. Below is a company's balance sheet data:

{document_text}

Your task is to analyze it and provide a structured summary in **tabular format only**.  

Generate tables for the following sections:

1. **Company & Period**  
   | Company | Period |

2. **Assets**  
   | Asset Type | Value | YoY Change / Trend |

3. **Liabilities**  
   | Liability Type | Value | YoY Change / Risk Factors |

4. **Borrowings**  
   | Borrowing Type | Value | Debt-to-Equity Impact |

5. **Reserves & Surplus**  
   | Reserve Type | Value | Contribution to Net Worth |

6. **Earnings / Net Worth**  
   | Metric | Value | Financial Strength |

7. **Overall Summary**  
   | Insight | Details |

⚠️ Output Rules:  
- Return tables in **Markdown tables** (or HTML tables if formatting better fits).  
- No JSON, no extra commentary, no explanations.
- Use `N/A` where information is missing.  
""")


# 1. **Company & Period**  
#    - Identify the company name and year(s) from the document text.  

# 2. **Assets**  
#    - Major components (current assets, fixed assets, investments, etc.).  
#    - Growth or decline compared to previous year(s).  

# 3. **Liabilities**  
#    - Breakdown (current liabilities, long-term liabilities).  
#    - Any major increase/decrease or risk factors.  

# 4. **Borrowings**  
#    - Short-term and long-term borrowings.  
#    - Debt-to-equity implications.  

# 5. **Reserves & Surplus**  
#    - General reserves, retained earnings, or other reserves.  
#    - Contribution to net worth.  

# 6. **Earnings/Net Worth**  
#    - Shareholder’s equity position.  
#    - Indication of company’s financial strength.  

# 7. **Overall Summary**  
#    - Key insights into company’s financial health.  
#    - Any red flags or strengths.  

# Return ONLY valid JSON matching the exact schema below.

# {format_instructions}
# """)

# Prompt for document comparison
document_comparison_prompt = ChatPromptTemplate.from_template("""
You will be provided with content from two PDFs. Your tasks are as follows:

1. Compare the content in two PDFs
2. Identify the difference in PDF and note down the page number 
3. The output you provide must be page wise comparison content 
4. If any page do not have any change, mention as 'NO CHANGE' 

Input documents:

{combined_docs}

Your response should follow this format:

{format_instruction}
""")

# Prompt for contextual question rewriting
contextualize_question_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Given a conversation history and the most recent user query, rewrite the query as a standalone question "
        "that makes sense without relying on the previous context. Do not provide an answer—only reformulate the "
        "question if necessary; otherwise, return it unchanged."
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Prompt for answering based on context
context_qa_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an assistant designed to answer questions using the provided context. Rely only on the retrieved "
        "information to form your response. If the answer is not found in the context, respond with 'I don't know.' "
        "Keep your answer concise and no longer than three sentences.\n\n{context}"
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Central dictionary to register prompts
PROMPT_REGISTRY = {
    "document_analysis": document_analysis_prompt,
    "document_comparison": document_comparison_prompt,
    "contextualize_question": contextualize_question_prompt,
    "context_qa": context_qa_prompt,
}
