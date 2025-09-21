from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# Food Truck Models
class MenuItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    available: bool = True

class Location(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    latitude: float
    longitude: float
    schedule: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LocationCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    schedule: Optional[str] = None
    active: bool = True

class FoodTruckInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    phone: str
    email: Optional[str] = None
    social_media: Optional[dict] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FoodTruckInfoCreate(BaseModel):
    name: str
    description: str
    phone: str
    email: Optional[str] = None
    social_media: Optional[dict] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# Food Truck routes
@api_router.get("/foodtruck", response_model=FoodTruckInfo)
async def get_food_truck_info():
    info = await db.food_truck_info.find_one()
    if not info:
        # Return default info if none exists
        default_info = {
            "id": str(uuid.uuid4()),
            "name": "Tasty Wheels Food Truck",
            "description": "Serving delicious street food with fresh ingredients and bold flavors",
            "phone": "(555) 123-4567",
            "email": "info@tastywheels.com",
            "social_media": {
                "instagram": "@tastywheels",
                "facebook": "TastyWheelsFoodTruck"
            },
            "created_at": datetime.utcnow()
        }
        return FoodTruckInfo(**default_info)
    return FoodTruckInfo(**info)

@api_router.put("/foodtruck", response_model=FoodTruckInfo)
async def update_food_truck_info(info: FoodTruckInfoCreate):
    existing = await db.food_truck_info.find_one()
    info_dict = info.dict()

    if existing:
        info_dict["id"] = existing["id"]
        info_dict["created_at"] = existing["created_at"]
        await db.food_truck_info.replace_one({"id": existing["id"]}, info_dict)
    else:
        info_obj = FoodTruckInfo(**info_dict)
        await db.food_truck_info.insert_one(info_obj.dict())
        return info_obj

    return FoodTruckInfo(**info_dict)

# Menu routes
@api_router.get("/menu", response_model=List[MenuItem])
async def get_menu():
    menu_items = await db.menu_items.find().to_list(1000)
    if not menu_items:
        # Return sample menu if none exists
        sample_menu = [
            {
                "id": str(uuid.uuid4()),
                "name": "Gourmet Burger",
                "description": "Juicy beef patty with fresh lettuce, tomato, and our special sauce",
                "price": 12.99,
                "category": "Burgers",
                "available": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Fish Tacos",
                "description": "Crispy fish with cabbage slaw and lime crema in soft tortillas",
                "price": 9.99,
                "category": "Tacos",
                "available": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Loaded Fries",
                "description": "Crispy fries topped with cheese, bacon, and green onions",
                "price": 7.99,
                "category": "Sides",
                "available": True,
                "created_at": datetime.utcnow()
            }
        ]
        return [MenuItem(**item) for item in sample_menu]
    return [MenuItem(**item) for item in menu_items]

@api_router.post("/menu", response_model=MenuItem)
async def create_menu_item(item: MenuItemCreate):
    item_obj = MenuItem(**item.dict())
    await db.menu_items.insert_one(item_obj.dict())
    return item_obj

@api_router.put("/menu/{item_id}", response_model=MenuItem)
async def update_menu_item(item_id: str, item: MenuItemCreate):
    item_dict = item.dict()
    existing = await db.menu_items.find_one({"id": item_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item_dict["id"] = item_id
    item_dict["created_at"] = existing["created_at"]
    await db.menu_items.replace_one({"id": item_id}, item_dict)
    return MenuItem(**item_dict)

@api_router.delete("/menu/{item_id}")
async def delete_menu_item(item_id: str):
    result = await db.menu_items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"success": True, "message": "Menu item deleted"}

# Location routes
@api_router.get("/locations", response_model=List[Location])
async def get_locations():
    locations = await db.locations.find().to_list(1000)
    if not locations:
        # Return sample locations if none exist
        sample_locations = [
            {
                "id": str(uuid.uuid4()),
                "name": "Downtown Plaza",
                "address": "123 Main St, Downtown",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "schedule": "Mon-Fri: 11:30AM-2:30PM",
                "active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Business District",
                "address": "456 Corporate Blvd",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "schedule": "Mon-Fri: 12:00PM-3:00PM",
                "active": True,
                "created_at": datetime.utcnow()
            }
        ]
        return [Location(**loc) for loc in sample_locations]
    return [Location(**loc) for loc in locations]

@api_router.post("/locations", response_model=Location)
async def create_location(location: LocationCreate):
    location_obj = Location(**location.dict())
    await db.locations.insert_one(location_obj.dict())
    return location_obj

@api_router.put("/locations/{location_id}", response_model=Location)
async def update_location(location_id: str, location: LocationCreate):
    location_dict = location.dict()
    existing = await db.locations.find_one({"id": location_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Location not found")

    location_dict["id"] = location_id
    location_dict["created_at"] = existing["created_at"]
    await db.locations.replace_one({"id": location_id}, location_dict)
    return Location(**location_dict)

@api_router.delete("/locations/{location_id}")
async def delete_location(location_id: str):
    result = await db.locations.delete_one({"id": location_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"success": True, "message": "Location deleted"}


# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
