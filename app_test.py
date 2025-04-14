from gradio_client import Client, handle_file

client = Client("shrey-14/Road-damage-detection")
result = client.predict(
		im=handle_file('usa.jpg'),
		api_name="/predict"
)
print(result)