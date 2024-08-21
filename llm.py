import time
import streamlit as st


async def call_summary(client, query, conversation_history) -> str:
    start_time = time.time()

    stream = await client.chat.completions.create(
        #
        # Required parameters
        #
        messages = conversation_history + [
            # conversation_history includes system prompt and chat history
            
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": query,
            },
        ],
        # The language model which will generate the completion.
        model="llama3-70b-8192",
        #
        # Optional parameters
        #
        # Controls randomness: lowering results in less random completions.
        # As the temperature approaches zero, the model will become
        # deterministic and repetitive.
        temperature=0.7,
        # The maximum number of tokens to generate. Requests can use up to
        # 2048 tokens shared between prompt and completion.
        max_tokens=1024,
        # Controls diversity via nucleus sampling: 0.5 means half of all
        # likelihood-weighted options are considered.
        top_p=1,
        # A stop sequence is a predefined or user-specified text string that
        # signals an AI to stop generating content, ensuring its responses
        # remain focused and concise. Examples include punctuation marks and
        # markers like "[end]".
        stop=None,
        # If set, partial message deltas will be sent.
        stream=True,
    )

    end_time = time.time()

    # Print the completion returned by the LLM.
    # print(chat_completion.choices[0].message.content)

    #response = chat_completion.choices[0].message.content
    elapsed_time = int((end_time - start_time) * 1000)
    print(f"LLM ({elapsed_time}ms): ")

    # with st.write():
    message_placeholder = st.empty()

    response = ""

    async def text_iterator():
        async for chunk in stream:
            nonlocal response
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="")
                response += delta.content
                message_placeholder.markdown(response + "")
                yield delta.content
        message_placeholder.markdown(response)

    # Iterate over the async generator
    async for _ in text_iterator():
        pass
    
    print()

    return response
