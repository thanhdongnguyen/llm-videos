from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class TemplateTranslate:

    SYSTEM = """
      Translate the following subtitle to {lang}. Keep the same format including the index, timestamp, and subtitle text.
      
      Subtitle:
      {content}   
    """

class TemplateChatRetriever:
    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\
     
    <Context>{context}</Context>"""

    SYSTEM = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                qa_system_prompt
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Question: {input}")
        ]
    )


