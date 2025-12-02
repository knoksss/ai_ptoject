"""
Модуль для анализа изображений одежды с использованием Ollama (LLaVA/Moondream)
"""
import base64
import os
import re
import json
import requests
from typing import Dict, Optional
from src.logger import info_logger, er_logger


class ClothesVLMAnalyzer:
    """Класс для анализа изображений одежды с помощью Ollama Vision Models"""
    
    def __init__(self):
        """Инициализация анализатора"""
        # Конфигурация Ollama
        self.api_url = os.environ.get('OLLAMA_API_URL', 'http://localhost:11434')
        self.api_key = os.environ.get('OLLAMA_API_KEY', '')  # Опционально для защищенных серверов
        self.model = os.environ.get('OLLAMA_MODEL', 'llava')  # llava или moondream
        self.timeout = int(os.environ.get('OLLAMA_TIMEOUT', '120'))  # Таймаут в секундах
        
        self.is_available = False
        self._check_availability()
    
    def _check_availability(self):
        """Проверка доступности Ollama API"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.api_url}/api/tags",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '').split(':')[0] for m in models]
                
                if self.model.split(':')[0] in model_names or any(self.model in name for name in model_names):
                    self.is_available = True
                    info_logger.info(f"Ollama доступен. Модель '{self.model}' найдена.")
                else:
                    info_logger.warning(
                        f"Модель '{self.model}' не найдена. Доступные модели: {model_names}"
                    )
                    # Пробуем найти альтернативную vision-модель
                    vision_models = ['llava', 'moondream', 'bakllava']
                    for vm in vision_models:
                        if any(vm in name for name in model_names):
                            self.model = vm
                            self.is_available = True
                            info_logger.info(f"Используем альтернативную модель: {self.model}")
                            break
            else:
                info_logger.warning(f"Ollama API недоступен. Код ответа: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            info_logger.warning(
                f"Не удалось подключиться к Ollama по адресу {self.api_url}. "
                "Убедитесь, что Ollama запущен."
            )
        except Exception as e:
            er_logger.error(f"Ошибка при проверке Ollama: {e}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Формирует заголовки для запроса к API"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Добавляем API-ключ если он задан
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        return headers
    
    def _encode_image(self, image_path: str) -> str:
        """Кодирует изображение в base64"""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_analysis_prompt(self) -> str:
        """Создает промпт для анализа одежды"""
        return """Look at this clothing photo carefully.

Tell me:
1. What clothing item? (t-shirt, jeans, dress, jacket, coat, puffer jacket, sweater, shirt, pants, skirt, hoodie, shoes, blouse, shorts)
2. Main color? (blue, black, white, red, green, gray, pink, beige, brown, orange, purple, yellow)
3. Brand logo or name visible? Which brand?
4. Material? (cotton, denim, leather, wool, polyester, nylon, down, synthetic)
5. Any TEXT, words, prints, or inscriptions on the clothing? Read them exactly.
6. Any patterns or design details? (stripes, logo print, graphic, plain, fur trim)

Reply ONLY with JSON:
{"category":"jacket","color":"black","brand":"","material":"nylon","text":"","style":"fur trim"}

If no text/brand visible, use empty string."""
    
    def analyze_image(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Анализирует изображение одежды и возвращает характеристики
        
        Args:
            image_path: путь к изображению
            
        Returns:
            Словарь с характеристиками одежды или None в случае ошибки
        """
        # Проверяем доступность при каждом вызове (на случай если Ollama запустился позже)
        if not self.is_available:
            self._check_availability()
        
        if not self.is_available:
            er_logger.warning("Ollama недоступен. Анализ невозможен.")
            return None
        
        try:
            info_logger.info(f"Анализ изображения: {image_path}")
            
            # Кодируем изображение в base64
            image_base64 = self._encode_image(image_path)
            
            # Формируем запрос к Ollama
            payload = {
                "model": self.model,
                "prompt": self._create_analysis_prompt(),
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Немного выше для лучшего распознавания
                    "num_predict": 300,  # Достаточно для JSON
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            headers = self._get_headers()
            
            info_logger.info(f"Отправка запроса к Ollama ({self.model})...")
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                er_logger.error(f"Ошибка Ollama API: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            generated_text = result.get('response', '')
            
            info_logger.info(f"Ответ модели: {generated_text[:200]}...")
            
            # Парсим JSON из ответа
            parsed_data = self._parse_ollama_response(generated_text)
            
            return parsed_data
            
        except requests.exceptions.Timeout:
            er_logger.error(f"Таймаут запроса к Ollama (>{self.timeout}с)")
            return None
        except Exception as e:
            er_logger.error(f"Ошибка анализа изображения: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_ollama_response(self, response_text: str) -> Dict[str, str]:
        """
        Парсит ответ от Ollama и извлекает данные об одежде
        
        Args:
            response_text: текстовый ответ от модели
            
        Returns:
            Словарь с извлеченными данными
        """
        # Пытаемся найти JSON в ответе
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        
        parsed = {}
        
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                info_logger.info(f"Распарсен JSON: {parsed}")
            except json.JSONDecodeError:
                info_logger.warning("Не удалось распарсить JSON, извлекаем данные вручную")
                parsed = self._extract_from_text(response_text)
        else:
            info_logger.warning("JSON не найден в ответе, извлекаем данные из текста")
            parsed = self._extract_from_text(response_text)
        
        # Маппинг категорий на русский (расширенный)
        category_names_ru = {
            't-shirt': 'Футболка',
            'tshirt': 'Футболка',
            't shirt': 'Футболка',
            'tee': 'Футболка',
            'shirt': 'Рубашка',
            'button-up': 'Рубашка',
            'button up': 'Рубашка',
            'jeans': 'Джинсы',
            'denim': 'Джинсы',
            'dress': 'Платье',
            'pants': 'Брюки',
            'trousers': 'Брюки',
            'slacks': 'Брюки',
            'skirt': 'Юбка',
            'jacket': 'Куртка',
            'puffer jacket': 'Куртка',
            'puffer': 'Куртка',
            'down jacket': 'Куртка',
            'blazer': 'Пиджак',
            'coat': 'Пальто',
            'overcoat': 'Пальто',
            'shoes': 'Обувь',
            'sneakers': 'Кроссовки',
            'trainers': 'Кроссовки',
            'boots': 'Ботинки',
            'sweater': 'Свитер',
            'jumper': 'Свитер',
            'pullover': 'Свитер',
            'hoodie': 'Толстовка',
            'sweatshirt': 'Толстовка',
            'blouse': 'Блузка',
            'top': 'Топ',
            'tank top': 'Майка',
            'shorts': 'Шорты',
            'cardigan': 'Кардиган',
            'vest': 'Жилет',
            'polo': 'Поло',
            'polo shirt': 'Поло',
        }
        
        # Извлекаем категорию
        category_raw = parsed.get('category', '').lower().strip()
        
        # Нормализуем категорию к значениям формы
        category_to_form = {
            't-shirt': 't-shirt',
            'tshirt': 't-shirt',
            't shirt': 't-shirt',
            'tee': 't-shirt',
            'shirt': 'shirt',
            'button-up': 'shirt',
            'button up': 'shirt',
            'blouse': 'blouse',
            'jeans': 'jeans',
            'denim': 'jeans',
            'dress': 'dress',
            'pants': 'pants',
            'trousers': 'pants',
            'slacks': 'pants',
            'skirt': 'skirt',
            'jacket': 'jacket',
            'puffer jacket': 'jacket',
            'puffer': 'jacket',
            'down jacket': 'jacket',
            'blazer': 'jacket',
            'coat': 'coat',
            'overcoat': 'coat',
            'shoes': 'shoes',
            'sneakers': 'sneakers',
            'trainers': 'sneakers',
            'boots': 'boots',
            'sweater': 'sweater',
            'jumper': 'sweater',
            'pullover': 'sweater',
            'hoodie': 'hoodie',
            'sweatshirt': 'hoodie',
            'shorts': 'shorts',
            'cardigan': 'sweater',
            'vest': 'jacket',
            'polo': 't-shirt',
            'polo shirt': 't-shirt',
            'top': 'blouse',
            'tank top': 't-shirt',
        }
        
        category = category_to_form.get(category_raw, category_raw)
        category_ru = category_names_ru.get(category_raw, category_names_ru.get(category, ''))
        
        # Извлекаем цвет (фильтруем шаблонные значения)
        color = parsed.get('color', '')
        color_placeholders = ['unknown', 'не определено', '', 'n/a', 'none', 'color', 'empty']
        if not color or color.lower().strip() in color_placeholders:
            color = self._extract_color_from_text(response_text)
        else:
            # Нормализуем цвет (переводим на русский если на английском)
            color_normalized = self._normalize_color(color)
            if color_normalized:
                color = color_normalized
        
        # Извлекаем материал (фильтруем шаблонные значения)
        material = parsed.get('material', '')
        material_placeholders = ['unknown', 'не определено', 'not visible', 'n/a', 'none',
                                 'material', 'empty', '', 'not found']
        if not material or material.lower().strip() in material_placeholders:
            material = ''
        else:
            # Переводим материал на русский
            material = self._normalize_material(material)
        
        # Джинсы обычно из денима
        if category in ['jeans', 'джинсы', 'denim'] and not material:
            material = 'Деним'
        
        # Извлекаем бренд (фильтруем шаблонные значения)
        brand = parsed.get('brand', '')
        placeholder_values = ['unknown', 'не определено', 'not visible', 'none', '', 
                              'brand', 'brand or empty', 'brand_or_empty', 'empty',
                              'n/a', 'no', 'no brand', 'not found']
        if brand.lower().strip() in placeholder_values:
            brand = ''
        
        # Извлекаем состояние
        condition = parsed.get('condition', 'good').lower()
        if condition not in ['new', 'excellent', 'good', 'satisfactory']:
            condition = 'good'
        
        # Извлекаем текст/надписи с одежды
        text_on_clothes = parsed.get('text', '')
        text_placeholders = ['', 'none', 'no text', 'empty', 'n/a', 'not visible', 
                            'no', 'unknown', 'text']
        if text_on_clothes.lower().strip() in text_placeholders:
            text_on_clothes = ''
        
        # Извлекаем стиль/узор
        style = parsed.get('style', '')
        style_placeholders = ['', 'none', 'plain', 'empty', 'n/a', 'style', 'unknown']
        if style.lower().strip() in style_placeholders:
            style = ''
        
        # Генерируем описание с учетом надписей
        description = self._generate_description_with_text(
            category_ru, color, material, text_on_clothes, style
        )
        
        # Генерируем название
        clothes_name = ''
        if category_ru:
            clothes_name = category_ru
            if color:
                clothes_name = f"{color} {category_ru.lower()}"
        
        result = {
            'clothes_category': category,
            'clothes_color': color,
            'clothes_material': material,
            'clothes_brand': brand,
            'clothes_description': description,
            'clothes_name': clothes_name,
            'clothes_condition': condition
        }
        
        info_logger.info(f"Результат парсинга: {result}")
        return result
    
    def _extract_from_text(self, text: str) -> Dict[str, str]:
        """Извлекает данные из текста без JSON"""
        text_lower = text.lower()
        result = {}
        
        # Извлекаем категорию
        categories = [
            ('t-shirt', ['t-shirt', 'tshirt', 't shirt', 'tee']),
            ('shirt', ['shirt', 'button-up', 'button up']),
            ('jeans', ['jeans', 'denim pants']),
            ('dress', ['dress']),
            ('pants', ['pants', 'trousers']),
            ('skirt', ['skirt']),
            ('jacket', ['jacket']),
            ('coat', ['coat']),
            ('sweater', ['sweater', 'jumper', 'pullover']),
            ('hoodie', ['hoodie', 'sweatshirt']),
            ('shoes', ['shoes', 'sneakers', 'boots']),
            ('shorts', ['shorts']),
        ]
        
        for cat, keywords in categories:
            if any(kw in text_lower for kw in keywords):
                result['category'] = cat
                break
        
        # Извлекаем цвет
        color = self._extract_color_from_text(text)
        if color:
            result['color'] = color
        
        # Извлекаем бренд
        brands = ['nike', 'adidas', 'puma', 'reebok', 'zara', 'h&m', 'uniqlo', 
                  'levi', 'levis', "levi's", 'gucci', 'prada', 'chanel', 'dior',
                  'versace', 'armani', 'calvin klein', 'tommy hilfiger', 'gap',
                  'mango', 'bershka', 'stradivarius', 'pull&bear', 'massimo dutti']
        for brand in brands:
            if brand in text_lower:
                result['brand'] = brand.title()
                break
        
        # Извлекаем материал
        materials = [
            ('cotton', ['cotton']),
            ('denim', ['denim']),
            ('leather', ['leather']),
            ('wool', ['wool', 'woolen']),
            ('silk', ['silk']),
            ('polyester', ['polyester', 'synthetic']),
        ]
        for mat, keywords in materials:
            if any(kw in text_lower for kw in keywords):
                result['material'] = mat
                break
        
        return result
    
    def _normalize_material(self, material: str) -> str:
        """Нормализует материал - переводит на русский если нужно"""
        material_lower = material.lower().strip()
        
        material_map = {
            'cotton': 'Хлопок',
            'denim': 'Деним',
            'leather': 'Кожа',
            'wool': 'Шерсть',
            'silk': 'Шелк',
            'linen': 'Лен',
            'polyester': 'Полиэстер',
            'nylon': 'Нейлон',
            'knit': 'Трикотаж',
            'knitted': 'Трикотаж',
            'synthetic': 'Синтетика',
            'velvet': 'Бархат',
            'satin': 'Атлас',
            'fleece': 'Флис',
            'cashmere': 'Кашемир',
            'suede': 'Замша',
        }
        
        # Если уже на русском
        russian_materials = ['хлопок', 'деним', 'кожа', 'шерсть', 'шелк', 'лен', 
                            'полиэстер', 'нейлон', 'трикотаж', 'синтетика']
        for rus in russian_materials:
            if rus in material_lower:
                return material.capitalize()
        
        return material_map.get(material_lower, material.capitalize() if material else '')
    
    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет - переводит на русский если нужно"""
        color_lower = color.lower().strip()
        
        color_map = {
            'white': 'Белый',
            'black': 'Черный',
            'blue': 'Синий',
            'light blue': 'Голубой',
            'sky blue': 'Голубой',
            'dark blue': 'Темно-синий',
            'navy': 'Темно-синий',
            'navy blue': 'Темно-синий',
            'red': 'Красный',
            'dark red': 'Бордовый',
            'burgundy': 'Бордовый',
            'green': 'Зеленый',
            'dark green': 'Темно-зеленый',
            'olive': 'Оливковый',
            'khaki': 'Хаки',
            'yellow': 'Желтый',
            'gray': 'Серый',
            'grey': 'Серый',
            'light gray': 'Светло-серый',
            'dark gray': 'Темно-серый',
            'brown': 'Коричневый',
            'pink': 'Розовый',
            'purple': 'Фиолетовый',
            'violet': 'Фиолетовый',
            'orange': 'Оранжевый',
            'beige': 'Бежевый',
            'cream': 'Кремовый',
            'tan': 'Бежевый',
            'gold': 'Золотой',
            'silver': 'Серебристый',
        }
        
        # Если уже на русском - возвращаем как есть (с заглавной буквы)
        russian_colors = ['белый', 'черный', 'синий', 'голубой', 'красный', 
                         'зеленый', 'желтый', 'серый', 'коричневый', 'розовый',
                         'фиолетовый', 'оранжевый', 'бежевый', 'темно-', 'светло-']
        
        for rus in russian_colors:
            if rus in color_lower:
                return color.capitalize()
        
        # Ищем английский цвет
        return color_map.get(color_lower, color.capitalize())
    
    def _extract_color_from_text(self, text: str) -> str:
        """Извлекает цвет из текста"""
        text_lower = text.lower()
        
        # Порядок важен - сначала более специфичные цвета
        colors = [
            # Составные цвета (проверяем первыми)
            ('light blue', 'Голубой'),
            ('sky blue', 'Голубой'),
            ('dark blue', 'Темно-синий'),
            ('navy blue', 'Темно-синий'),
            ('navy', 'Темно-синий'),
            ('dark green', 'Темно-зеленый'),
            ('olive', 'Оливковый'),
            ('khaki', 'Хаки'),
            ('dark red', 'Бордовый'),
            ('burgundy', 'Бордовый'),
            ('maroon', 'Бордовый'),
            ('light gray', 'Светло-серый'),
            ('dark gray', 'Темно-серый'),
            ('charcoal', 'Темно-серый'),
            ('light grey', 'Светло-серый'),
            ('dark grey', 'Темно-серый'),
            ('hot pink', 'Ярко-розовый'),
            ('light pink', 'Светло-розовый'),
            ('cream', 'Кремовый'),
            ('ivory', 'Слоновая кость'),
            ('tan', 'Бежевый'),
            ('camel', 'Бежевый'),
            # Русские составные
            ('темно-синий', 'Темно-синий'),
            ('светло-серый', 'Светло-серый'),
            ('темно-серый', 'Темно-серый'),
            ('темно-зеленый', 'Темно-зеленый'),
            # Базовые цвета
            ('white', 'Белый'),
            ('black', 'Черный'),
            ('blue', 'Синий'),
            ('red', 'Красный'),
            ('green', 'Зеленый'),
            ('yellow', 'Желтый'),
            ('gray', 'Серый'),
            ('grey', 'Серый'),
            ('brown', 'Коричневый'),
            ('pink', 'Розовый'),
            ('purple', 'Фиолетовый'),
            ('violet', 'Фиолетовый'),
            ('orange', 'Оранжевый'),
            ('beige', 'Бежевый'),
            ('gold', 'Золотой'),
            ('silver', 'Серебристый'),
            # Русские базовые
            ('белый', 'Белый'),
            ('черный', 'Черный'),
            ('синий', 'Синий'),
            ('голубой', 'Голубой'),
            ('красный', 'Красный'),
            ('зеленый', 'Зеленый'),
            ('желтый', 'Желтый'),
            ('серый', 'Серый'),
            ('коричневый', 'Коричневый'),
            ('розовый', 'Розовый'),
            ('фиолетовый', 'Фиолетовый'),
            ('оранжевый', 'Оранжевый'),
            ('бежевый', 'Бежевый'),
        ]
        
        for color_key, color_ru in colors:
            if color_key in text_lower:
                return color_ru
        
        return ''
    
    def _generate_description_with_text(self, category: str, color: str, material: str, 
                                         text_on_clothes: str, style: str) -> str:
        """Генерирует описание с учетом надписей на одежде"""
        parts = []
        placeholders = ['color', 'material', 'brand', 'category', 'type', 'empty', 'unknown']
        
        # Базовое описание
        if color and color.lower() not in placeholders:
            parts.append(color)
        
        if category and category.lower() not in placeholders:
            parts.append(category.lower())
        
        if material and material.lower() not in placeholders:
            parts.append(f"из {material.lower()}")
        
        # Добавляем стиль/узор
        if style and style.lower() not in placeholders:
            style_ru = self._translate_style(style)
            if style_ru:
                parts.append(f"({style_ru})")
        
        # Добавляем надпись если есть
        if text_on_clothes and text_on_clothes.lower() not in placeholders:
            parts.append(f'с надписью "{text_on_clothes}"')
        
        if parts:
            description = ' '.join(parts)
            return description[0].upper() + description[1:]
        
        return ''
    
    def _translate_style(self, style: str) -> str:
        """Переводит стиль на русский"""
        style_lower = style.lower().strip()
        style_map = {
            'logo print': 'с логотипом',
            'logo': 'с логотипом',
            'graphic': 'с принтом',
            'graphic print': 'с принтом',
            'print': 'с принтом',
            'stripes': 'в полоску',
            'striped': 'в полоску',
            'checkered': 'в клетку',
            'plaid': 'в клетку',
            'floral': 'с цветами',
            'polka dot': 'в горошек',
            'dots': 'в горошек',
            'solid': 'однотонный',
            'plain': '',
            'pattern': 'с узором',
            'embroidered': 'с вышивкой',
            'vintage': 'винтажный',
        }
        return style_map.get(style_lower, style)
    
    def _generate_description(self, category: str, color: str, material: str) -> str:
        """Генерирует описание на основе имеющихся данных"""
        parts = []
        
        # Фильтруем шаблонные значения
        placeholders = ['color', 'material', 'brand', 'category', 'type', 'empty', 'unknown']
        
        if color and color.lower() not in placeholders:
            parts.append(color)
        
        if category and category.lower() not in placeholders:
            parts.append(category.lower())
        
        if material and material.lower() not in placeholders:
            parts.append(f"из {material.lower()}")
        
        if parts:
            description = ' '.join(parts)
            return description[0].upper() + description[1:]
        
        return ''


# Глобальный экземпляр анализатора
_analyzer_instance = None


def get_analyzer() -> ClothesVLMAnalyzer:
    """Получить экземпляр анализатора (singleton)"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ClothesVLMAnalyzer()
    return _analyzer_instance
