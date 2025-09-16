"""
AWS Bedrock service for AI integration.
Provides text generation and embeddings functionality.
"""
import logging
import json
from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.config.settings import settings

logger = logging.getLogger(__name__)


class BedrockService:
    """
    AWS Bedrock service for AI operations.
    Handles text generation and embeddings using AWS Bedrock models.
    """
    
    def __init__(self):
        """
        Initialize Bedrock service.
        Automatically detects credentials based on environment.
        """
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Initialize Bedrock client with appropriate credentials.
        Production: Uses EC2 IAM role or default boto3 credential chain
        Local: Uses environment variables
        """
        try:
            if settings.is_production:
                # Production: Use default credential chain (EC2 IAM role, etc.)
                self.client = boto3.client(
                    'bedrock-runtime',
                    region_name=settings.aws_region
                )
                logger.info("Initialized Bedrock client with default credentials (production)")
            else:
                # Local: Use explicit credentials if provided
                if settings.aws_access_key_id and settings.aws_secret_access_key:
                    self.client = boto3.client(
                        'bedrock-runtime',
                        region_name=settings.aws_region,
                        aws_access_key_id=settings.aws_access_key_id,
                        aws_secret_access_key=settings.aws_secret_access_key
                    )
                    logger.info("Initialized Bedrock client with explicit credentials (local)")
                else:
                    # Fallback to default credential chain
                    self.client = boto3.client(
                        'bedrock-runtime',
                        region_name=settings.aws_region
                    )
                    logger.info("Initialized Bedrock client with default credentials (local fallback)")
                    
        except NoCredentialsError:
            logger.warning("No AWS credentials found. Bedrock functionality will be limited.")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Bedrock client: {e}")
            self.client = None
    
    def generate_text(
        self,
        prompt: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate text using AWS Bedrock.
        
        Args:
            prompt: Input prompt for text generation
            model_id: Bedrock model ID to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text or None if error
        """
        if not self.client:
            logger.error("Bedrock client not initialized")
            return None
        
        try:
            # Prepare request body based on model type
            if "anthropic.claude" in model_id:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            else:
                # Generic format for other models
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature
                    }
                }
            
            # Make request to Bedrock
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if "anthropic.claude" in model_id:
                return response_body.get('content', [{}])[0].get('text', '')
            else:
                return response_body.get('results', [{}])[0].get('outputText', '')
                
        except ClientError as e:
            logger.error(f"AWS Bedrock client error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating text with Bedrock: {e}")
            return None
    
    def generate_embeddings(
        self,
        texts: List[str],
        model_id: str = "amazon.titan-embed-text-v1"
    ) -> Optional[List[List[float]]]:
        """
        Generate embeddings for text using AWS Bedrock.
        
        Args:
            texts: List of texts to generate embeddings for
            model_id: Bedrock embedding model ID
            
        Returns:
            List of embedding vectors or None if error
        """
        if not self.client:
            logger.error("Bedrock client not initialized")
            return None
        
        try:
            embeddings = []
            
            for text in texts:
                body = {
                    "inputText": text
                }
                
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json"
                )
                
                response_body = json.loads(response['body'].read())
                embedding = response_body.get('embedding', [])
                embeddings.append(embedding)
            
            return embeddings
            
        except ClientError as e:
            logger.error(f"AWS Bedrock client error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating embeddings with Bedrock: {e}")
            return None
    
    def summarize_text(
        self,
        text: str,
        max_length: int = 200,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ) -> Optional[str]:
        """
        Summarize text using AWS Bedrock.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            model_id: Bedrock model ID to use
            
        Returns:
            Summary text or None if error
        """
        prompt = f"""Please provide a concise summary of the following text in no more than {max_length} characters:

{text}

Summary:"""
        
        return self.generate_text(
            prompt=prompt,
            model_id=model_id,
            max_tokens=max_length // 4,  # Rough token estimation
            temperature=0.3
        )
    
    def analyze_sentiment(
        self,
        text: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment of text using AWS Bedrock.
        
        Args:
            text: Text to analyze
            model_id: Bedrock model ID to use
            
        Returns:
            Sentiment analysis result or None if error
        """
        prompt = f"""Analyze the sentiment of the following text and respond with a JSON object containing:
- sentiment: "positive", "negative", or "neutral"
- confidence: a number between 0 and 1
- explanation: brief explanation of the sentiment

Text: {text}

Response (JSON only):"""
        
        try:
            response = self.generate_text(
                prompt=prompt,
                model_id=model_id,
                max_tokens=200,
                temperature=0.1
            )
            
            if response:
                # Try to parse JSON response
                return json.loads(response.strip())
            
            return None
            
        except json.JSONDecodeError:
            logger.error("Failed to parse sentiment analysis JSON response")
            return None
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if Bedrock service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        return self.client is not None 