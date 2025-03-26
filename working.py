import google.generativeai as genai

genai.configure(api_key="AIzaSyCyl7sHG3M7XVTx1tcWfarfzWPhGHvqlYk")

# model = genai.GenerativeModel(model_name="models/gemini-pro")  # Correct format
# response = model.generate_content("Hello, how are you?")
# print(response.text)

# List available models
# models = genai.list_models()
# for model in models:
#     print(model.name)


# Use an available model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

response = model.generate_content("can u write code of binary search in python")
print(response.text)
