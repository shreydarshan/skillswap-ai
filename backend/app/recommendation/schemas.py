import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class ReciprocalMatchScores(BaseModel):
    """
    Directional and reciprocal matching scores between two users.
    All scores are normalized between 0.0 and 1.0.
    """
    forward_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="A_WANTS_B_OFFERS: directional cosine similarity of user A wanted skills vs user B offered skills"
    )
    reverse_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="A_OFFERS_B_WANTS: directional cosine similarity of user A offered skills vs user B wanted skills"
    )
    reciprocal_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="RECIPROCAL_SCORE: (forward_score + reverse_score) / 2"
    )


class SkillDetail(BaseModel):
    """
    Structured skill representation for UI presentation.
    """
    id: Optional[str] = None
    name: str
    category: Optional[str] = "General"
    level: Optional[str] = None
    urgency: Optional[str] = None


class CandidateRecommendation(BaseModel):
    """
    Structured recommendation candidate with profile info, reciprocal match scores,
    and transparent explanation breakdown of skill overlap.
    Excludes sensitive authentication or security attributes.
    """
    user_id: uuid.UUID
    candidate_id: Optional[str] = None
    full_name: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar: Optional[str] = None
    college: Optional[str] = None
    university: Optional[str] = None
    branch: Optional[str] = None
    major: Optional[str] = None
    role: Optional[str] = None
    year: Optional[int] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    gender_preference: Optional[str] = None
    is_demo: bool = False
    is_test: bool = False
    skills_offered: List[str] = Field(default_factory=list)
    skills_wanted: List[str] = Field(default_factory=list)
    skillsOffered: List[SkillDetail] = Field(default_factory=list)
    skillsWanted: List[SkillDetail] = Field(default_factory=list)
    match_scores: ReciprocalMatchScores
    reciprocal_score: float = 0.0
    forward_score: float = 0.0
    reverse_score: float = 0.0
    match_percentage: int = 0
    matching_wanted_skills: List[str] = Field(
        default_factory=list,
        description="Skills candidate offers that the user wants to learn (A_wants ∩ B_offers)"
    )
    matching_offered_skills: List[str] = Field(
        default_factory=list,
        description="Skills user offers that the candidate wants to learn (A_offers ∩ B_wants)"
    )
    match_reasons: List[str] = Field(
        default_factory=list,
        description="Transparent explanations of skill compatibility"
    )


class ReciprocalMatchSimulationRequest(BaseModel):
    """
    Schema for simulating or testing reciprocal match between two arbitrary skill sets.
    """
    user_a_offers: List[str] = Field(default_factory=list)
    user_a_wants: List[str] = Field(default_factory=list)
    user_b_offers: List[str] = Field(default_factory=list)
    user_b_wants: List[str] = Field(default_factory=list)


class CollaborativeCandidateRecommendation(BaseModel):
    """
    Structured collaborative recommendation candidate based on genuine interaction history.
    """
    candidate_id: uuid.UUID
    candidate_name: str
    collaborative_score: float = Field(..., ge=0.0, le=1.0, description="Normalized collaborative score [0, 1]")
    similar_user_count: int = Field(..., description="Number of similar students contributing collaborative evidence")
    interaction_evidence_count: int = Field(..., description="Total interaction records backing this recommendation")
    explanation: str = Field(..., description="Transparent, non-ML explanation of why this candidate was recommended")
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    bio: Optional[str] = None
    skills_offered: List[str] = Field(default_factory=list)
    skills_wanted: List[str] = Field(default_factory=list)
    is_demo: bool = False


class HybridCandidateRecommendation(BaseModel):
    """
    Structured hybrid recommendation candidate combining Stage 5A/5B content-based
    reciprocal compatibility and Stage 5D user-user collaborative filtering signals.
    """
    candidate_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    candidate_name: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar: Optional[str] = None
    college: Optional[str] = None
    university: Optional[str] = None
    branch: Optional[str] = None
    major: Optional[str] = None
    role: Optional[str] = None
    year: Optional[int] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    gender_preference: Optional[str] = None
    skills_offered: List[str] = Field(default_factory=list)
    skills_wanted: List[str] = Field(default_factory=list)
    skillsOffered: List[SkillDetail] = Field(default_factory=list)
    skillsWanted: List[SkillDetail] = Field(default_factory=list)

    # Component & Combined Scores [0.0, 1.0]
    content_score: float = Field(..., ge=0.0, le=1.0, description="Stage 5A content reciprocal score")
    collaborative_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Stage 5D collaborative score (None if cold-start)")
    hybrid_score: float = Field(..., ge=0.0, le=1.0, description="Final combined hybrid score")

    # Match Percentages [0, 100]
    content_match_percentage: int = Field(..., ge=0, le=100)
    collaborative_match_percentage: Optional[int] = Field(None, ge=0, le=100)
    hybrid_match_percentage: int = Field(..., ge=0, le=100)
    match_percentage: int = Field(..., ge=0, le=100)  # Primary display percentage

    # Explanations
    content_match_reasons: List[str] = Field(default_factory=list)
    match_reasons: List[str] = Field(default_factory=list)
    collaborative_explanation: Optional[str] = None
    recommendation_explanation: str
    is_collaborative_available: bool = False

    # Collaborative Evidence
    similar_user_count: int = 0
    interaction_evidence_count: int = 0

    # Detailed skill overlap for WhyMatch modal compatibility
    matching_wanted_skills: List[str] = Field(default_factory=list)
    matching_offered_skills: List[str] = Field(default_factory=list)
    forward_score: float = 0.0
    reverse_score: float = 0.0
    reciprocal_score: float = 0.0

    is_demo: bool = False
    is_test: bool = False
