import gradio as gr
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

# Загрузка данных
with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

print(f"Загружено {len(articles)} статей")

# Инициализация модели
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Подготовка данных
documents = []
for article in articles:
    documents.append({
        'name': article['name'],
        'content': article['content'][:1000],
        'full_content': article['content']
    })

# Создание эмбеддингов
print("Создание эмбеддингов...")
document_embeddings = model.encode([doc['content'] for doc in documents])
print("Эмбеддинги готовы!")

def semantic_search(query: str, top_k: int = 5) -> List[Dict]:
    query_embedding = model.encode([query])
    similarities = np.dot(document_embeddings, query_embedding.T).flatten()
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            'name': documents[idx]['name'],
            'full_content': documents[idx]['full_content'],
            'similarity': float(similarities[idx])
        })
    
    return results

def create_document_accordions(results: List[Dict]):
    """Создает раскрывающиеся окна для документов"""
    accordions = []
    for i, result in enumerate(results, 1):
        with gr.Accordion(label=f"{i}. {result['name']} (сходство: {result['similarity']:.3f})", open=False):
            gr.Textbox(
                value=result['full_content'],
                label="",
                lines=8,
                max_lines=15,
                interactive=False
            )
    return accordions

def rag_query(query: str, top_k: int = 3):
    if not query.strip():
        return "Пожалуйста, введите вопрос", None
    
    try:
        results = semantic_search(query, top_k=top_k)
        
        answer = f"**Вопрос:** {query}\n\n"
        answer += f"**Найдено релевантных документов:** {len(results)}\n\n"
        answer += "**Ответ:**\n"
        
        if results:
            answer += "Вот наиболее релевантные документы из базы знаний:\n\n"
            for i, result in enumerate(results, 1):
                answer += f"{i}. **{result['name']}** (сходство: {result['similarity']:.3f})\n"
        else:
            answer += "Релевантных документов не найдено."
        
        return answer, gr.Column(visible=bool(results))
        
    except Exception as e:
        return f"Ошибка: {str(e)}", None

# Создание интерфейса
with gr.Blocks(theme=gr.themes.Soft(), title="RAG Search") as demo:
    gr.Markdown("# 🔍 Поиск по научным статьям")
    gr.Markdown(f"*База данных: {len(articles)} статей*")
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="Ваш вопрос",
                placeholder="Задайте вопрос по теме научных статей...",
                lines=2
            )
            top_k_slider = gr.Slider(1, 5, value=3, label="Количество документов")
            search_btn = gr.Button("🔍 Поиск", variant="primary")
        
        with gr.Column():
            answer_output = gr.Textbox(label="Результат поиска", lines=6)
    
    # Динамические раскрывающиеся окна для документов
    documents_section = gr.Column(visible=False, key="Найденные документы")
    
    # Создаем несколько заранее подготовленных аккордеонов
    accordions = []
    for i in range(5):  # Максимум 5 документов
        with documents_section:
            accordion = gr.Accordion(visible=False, label=f"Документ {i+1}")
            with accordion:
                content_box = gr.Textbox(visible=False, lines=8, interactive=False)
            accordions.append((accordion, content_box))
    
    def update_results(query, top_k):
        answer, show_docs = rag_query(query, top_k)
        
        # Получаем реальные результаты
        results = semantic_search(query, top_k) if query.strip() else []
        
        updates = [answer, show_docs or gr.Column(visible=False)]
        
        # Обновляем аккордеоны
        for i in range(5):
            if i < len(results):
                updates.extend([
                    gr.Accordion(visible=True, label=f"{i+1}. {results[i]['name']} ({results[i]['similarity']:.3f})"),
                    gr.Textbox(visible=True, value=results[i]['full_content'])
                ])
            else:
                updates.extend([
                    gr.Accordion(visible=False),
                    gr.Textbox(visible=False)
                ])
        
        return updates
    
    search_btn.click(
        fn=update_results,
        inputs=[query_input, top_k_slider],
        outputs=[answer_output, documents_section] + 
                [comp for pair in accordions for comp in pair]
    )
    
    gr.Examples(
        examples=[
            ["Искусственный интеллект и машинное обучение"],
            ["Методы анализа больших данных"],
            ["Нейронные сети и глубокое обучение"],
            ["Научные исследования в компьютерном зрении"]
        ],
        inputs=query_input
    )

if __name__ == "__main__":
    demo.launch(server_port=7860)