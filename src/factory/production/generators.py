import hashlib
import random
from typing import List, Dict, Any, Tuple

def _get_seed(identifier: str) -> int:
    return int(hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:8], 16)

class DeterministicOfferGenerators:
    """
    Motores determinísticos de geração de cópia e metadados para a Offer Factory.
    Garantem 100% de reprodutibilidade para qualquer oportunidade.
    """

    @staticmethod
    def generate_headlines(niche: str, product_name: str, identifier: str) -> Tuple[str, str]:
        rng = random.Random(_get_seed(identifier + "_headline"))
        templates = [
            (f"Descubra Como Dominar {niche.title()} Com O Método {product_name}", "A solução passo a passo comprovada para obter resultados reais em tempo recorde."),
            (f"O Segredo Definitivo de {niche.title()} Revelado em {product_name}", "Chega de perder tempo com estratégias que não funcionam. Alcance o próximo nível hoje."),
            (f"Transforme Seus Resultados em {niche.title()} Com {product_name}", "Acelere seu aprendizado com um método 100% prático e direto ao ponto."),
            (f"Conquiste a Liberdade em {niche.title()} Através do {product_name}", "O guia definitivo usado pelos maiores especialistas do mercado."),
        ]
        return rng.choice(templates)

    @staticmethod
    def generate_benefits(niche: str, product_name: str, identifier: str) -> List[str]:
        rng = random.Random(_get_seed(identifier + "_benefits"))
        pool = [
            f"Acesso imediato e vitalício a todo o conteúdo do {product_name}.",
            f"Método prático e direto ao ponto no nicho de {niche.title()}.",
            "Modelos e templates 100% editáveis prontos para uso.",
            "Suporte dedicado e comunidade exclusiva de alunos.",
            "Garantia incondicional de satisfação ou reembolso total.",
            "Certificado de conclusão reconhecido para enriquecer seu currículo."
        ]
        return rng.sample(pool, k=4)

    @staticmethod
    def generate_pain_points(niche: str, identifier: str) -> List[str]:
        rng = random.Random(_get_seed(identifier + "_pain"))
        pool = [
            f"Frustração por tentar aprender {niche.title()} sozinho sem uma metodologia clara.",
            "Falta de tempo para consumir cursos longos e cheios de teoria inútil.",
            "Medo de investir em treinamentos ultrapassados e sem suporte.",
            f"Dificuldade de aplicar os conceitos de {niche.title()} no dia a dia com segurança."
        ]
        return rng.sample(pool, k=3)

    @staticmethod
    def generate_cta(identifier: str) -> Tuple[str, str]:
        rng = random.Random(_get_seed(identifier + "_cta"))
        ctas = [
            ("Garantir Minha Vaga Com Desconto Especial", "⚡ Restam poucas unidades com valor promocional!"),
            ("Quero Acesso Imediato Ao Método", "🔒 Compra 100% segura e acesso liberado na hora."),
            ("Aproveitar Oferta Por Tempo Limitado", "⏳ Esta condição especial expira em breve!"),
        ]
        return rng.choice(ctas)

    @staticmethod
    def generate_seo_metadata(niche: str, product_name: str, identifier: str) -> Dict[str, str]:
        return {
            "title": f"{product_name} — Site Oficial & Oferta Exclusiva",
            "description": f"Adquira o {product_name} no nicho de {niche} com garantia incondicional de 7 dias, bônus exclusivos e acesso imediato.",
            "canonical_url": f"https://pages.airevenueos.com/offer/{identifier}",
            "og_title": f"{product_name} | Oferta Oficial",
            "og_description": f"Aprenda {niche} com o método prático {product_name}.",
            "og_image": f"https://pages.airevenueos.com/assets/{identifier}_og.png"
        }

    @staticmethod
    def generate_keywords(niche: str, product_name: str, identifier: str) -> List[str]:
        base_kw = [niche.lower(), product_name.lower(), f"curso {niche}", f"guia {niche}", f"{product_name} funciona", f"{product_name} vale a pena"]
        return list(dict.fromkeys(base_kw))

    @staticmethod
    def generate_image_prompts(niche: str, product_name: str, identifier: str) -> List[Dict[str, str]]:
        rng = random.Random(_get_seed(identifier + "_img"))
        prompts = [
            {
                "type": "hero_background",
                "prompt": f"Professional modern digital workstation centered around {niche}, sleek lighting, high detail, 8k resolution, photorealistic, vibrant color palette",
                "aspect_ratio": "16:9"
            },
            {
                "type": "product_mockup",
                "prompt": f"3D floating digital product mockup box for {product_name}, clean glassmorphic style, glowing elements, professional branding design",
                "aspect_ratio": "1:1"
            },
            {
                "type": "pinterest_pin",
                "prompt": f"Vertical aesthetic Pinterest pin image about {niche}, clear text overlay space, warm cinematic lighting, high click-through rate design",
                "aspect_ratio": "9:16"
            }
        ]
        return prompts

    @staticmethod
    def generate_video_prompts(niche: str, product_name: str, identifier: str) -> Dict[str, Any]:
        return {
            "format": "vertical_9_16",
            "target_duration_sec": 45,
            "voiceover_script": f"Você também sente dificuldade para evoluir em {niche}? Conheça o {product_name}, o método passo a passo feito para você dominar esse mercado sem perder tempo. Clique no link e garanta seu acesso!",
            "b_roll_queries": [f"{niche} technology", f"person working on {niche}", "success business celebration"],
            "caption_style": "bold_yellow_subtitles",
            "music_mood": "upbeat_energetic"
        }

    @staticmethod
    def generate_landing_metadata(niche: str, product_name: str, headline: str, val_prop: str, benefits: List[str], pain_points: List[str], identifier: str) -> Dict[str, Any]:
        return {
            "theme": "dark_glassmorphism",
            "hero_section": {
                "headline": headline,
                "subheadline": val_prop,
                "cta_button_text": "Começar Agora"
            },
            "features_section": {
                "title": "Por que este método é diferente?",
                "items": benefits
            },
            "pain_points_section": {
                "title": "Você se identifica com algum desses problemas?",
                "items": pain_points
            },
            "pricing_section": {
                "original_price": "R$ 297,00",
                "discount_price": "R$ 97,00",
                "discount_badge": "67% OFF"
            }
        }

    @staticmethod
    def generate_pinterest_metadata(niche: str, product_name: str, identifier: str) -> Dict[str, Any]:
        return {
            "pin_title": f"Descubra o Método {product_name} para {niche.title()} 🚀",
            "pin_description": f"Aprenda passo a passo como dominar {niche} de forma prática e rápida com o {product_name}. Clique para saber mais!",
            "board_name": f"Dicas e Guias de {niche.title()}",
            "hashtags": [f"#{niche.replace(' ', '')}", f"#{product_name.replace(' ', '')}", "#dicas", "#desenvolvimento"],
            "destination_url": f"https://pages.airevenueos.com/offer/{identifier}"
        }

    @staticmethod
    def generate_analytics_metadata(opportunity_id: str, marketplace: str, niche: str, identifier: str) -> Dict[str, Any]:
        return {
            "ga4_event_name": "view_offer_page",
            "posthog_event": "offer_landed",
            "utm_params": {
                "utm_source": "pinterest",
                "utm_medium": "organic_pin",
                "utm_campaign": f"camp_{niche.lower()}",
                "utm_content": opportunity_id
            },
            "tracking_pixel_id": f"PIXEL_{identifier[:8]}"
        }
