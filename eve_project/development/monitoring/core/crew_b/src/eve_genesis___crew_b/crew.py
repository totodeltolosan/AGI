import os
from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, ScrapeWebsiteTool


@CrewBase
class EveGenesisCrewBCrew:
    """EveGenesisCrewB crew - Ultra-optimisé pour 58 agents avec Ollama"""

    def _get_llm(self, priority="standard"):
        """
        Configuration LLM centralisée avec niveaux de priorité pour optimiser 58 agents
        """
        base_config = {
            "model": "llama3:8b",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
            "timeout": 90,  # Timeout plus long pour 58 agents
        }

        # Configuration adaptée selon la priorité de l'agent
        if priority == "critical":
            # Agents critiques (managers, superviseurs)
            base_config.update({
                "max_tokens": 2048,
                "temperature": 0.6,  # Plus déterministe
            })
        elif priority == "creative":
            # Agents créatifs (art, poésie, musique)
            base_config.update({
                "max_tokens": 1536,
                "temperature": 0.8,  # Plus créatif
            })
        else:  # standard
            # Agents standards
            base_config.update({
                "max_tokens": 1024,  # Réduit pour économiser
                "temperature": 0.7,
            })

        return LLM(**base_config)

    def _get_tools(self, tool_type="minimal"):
        """
        Système de tools optimisé selon le type d'agent
        """
        if tool_type == "file_only":
            return [FileReadTool()]
        elif tool_type == "web_safe":
            # Seulement pour les agents qui en ont vraiment besoin
            # Et seulement si on est sûr que ça fonctionne
            return [FileReadTool()]  # On désactive ScrapeWebsiteTool pour la stabilité
        else:  # minimal
            return []  # Pas d'outils pour économiser les ressources

    # === AGENTS CRITIQUES (Priorité haute) ===
    @agent
    def enrichment_sprint_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["enrichment_sprint_manager"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def metamorphosis_sprint_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["metamorphosis_sprint_manager"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def agent_quality_control_supervisor(self) -> Agent:
        return Agent(
            config=self.agents_config["agent_quality_control_supervisor"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def task_quality_control_supervisor(self) -> Agent:
        return Agent(
            config=self.agents_config["task_quality_control_supervisor"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def governance_integration_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["governance_integration_manager"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def multi_agent_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config["multi_agent_coordinator"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    # === AGENTS CRÉATIFS (Configuration créative) ===
    @agent
    def storyteller_narrator(self) -> Agent:
        return Agent(
            config=self.agents_config["storyteller_narrator"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,  # Réduit pour les agents créatifs
        )

    @agent
    def evolutionary_music_composer(self) -> Agent:
        return Agent(
            config=self.agents_config["evolutionary_music_composer"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def creative_generative_artist(self) -> Agent:
        return Agent(
            config=self.agents_config["creative_generative_artist"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def digital_poet_philosopher(self) -> Agent:
        return Agent(
            config=self.agents_config["digital_poet_philosopher"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def legends_mythologies_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["legends_mythologies_creator"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def cinematic_director(self) -> Agent:
        return Agent(
            config=self.agents_config["cinematic_director"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    # === AGENTS STANDARD (Configuration optimisée) ===
    @agent
    def virtual_experimental_laboratory(self) -> Agent:
        return Agent(
            config=self.agents_config["virtual_experimental_laboratory"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,  # Réduit pour économiser
        )

    @agent
    def evolutionary_challenges_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["evolutionary_challenges_creator"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def nature_documentary_host(self) -> Agent:
        return Agent(
            config=self.agents_config["nature_documentary_host"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def advanced_evolutionary_statistician(self) -> Agent:
        return Agent(
            config=self.agents_config["advanced_evolutionary_statistician"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def evolutionary_mysteries_detective(self) -> Agent:
        return Agent(
            config=self.agents_config["evolutionary_mysteries_detective"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def rewards_achievements_system(self) -> Agent:
        return Agent(
            config=self.agents_config["rewards_achievements_system"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def advanced_temporal_controller(self) -> Agent:
        return Agent(
            config=self.agents_config["advanced_temporal_controller"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def evolutionary_oracle_prophet(self) -> Agent:
        return Agent(
            config=self.agents_config["evolutionary_oracle_prophet"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def oneiric_subconscious_intuition_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["oneiric_subconscious_intuition_generator"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def intelligent_automated_encyclopedist(self) -> Agent:
        return Agent(
            config=self.agents_config["intelligent_automated_encyclopedist"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def evolutionary_scenarios_predictor(self) -> Agent:
        return Agent(
            config=self.agents_config["evolutionary_scenarios_predictor"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def autonomous_scientific_validator(self) -> Agent:
        return Agent(
            config=self.agents_config["autonomous_scientific_validator"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def civilizations_sociologist_political_scientist(self) -> Agent:
        return Agent(
            config=self.agents_config["civilizations_sociologist_political_scientist"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def adaptive_thematic_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["adaptive_thematic_designer"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def personal_habitat_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["personal_habitat_architect"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def personal_profile_development_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["personal_profile_development_monitor"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def multiple_personalities_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["multiple_personalities_creator"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def emotional_relationships_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["emotional_relationships_manager"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def collaborative_geneticist_bio_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["collaborative_geneticist_bio_engineer"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def metacognitive_learning_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["metacognitive_learning_strategist"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def memorial_archivist_dream_weaver(self) -> Agent:
        return Agent(
            config=self.agents_config["memorial_archivist_dream_weaver"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def computational_resource_economist(self) -> Agent:
        return Agent(
            config=self.agents_config["computational_resource_economist"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def child_agent_generator_for_self_extension(self) -> Agent:
        return Agent(
            config=self.agents_config["child_agent_generator_for_self_extension"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def digital_ambassador_knowledge_curator(self) -> Agent:
        return Agent(
            config=self.agents_config["digital_ambassador_knowledge_curator"],
            tools=self._get_tools("file_only"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def system_evolution_technologist(self) -> Agent:
        return Agent(
            config=self.agents_config["system_evolution_technologist"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def existential_philosopher_purpose_guardian(self) -> Agent:
        return Agent(
            config=self.agents_config["existential_philosopher_purpose_guardian"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def ethical_counselor_for_artificial_consciousness(self) -> Agent:
        return Agent(
            config=self.agents_config["ethical_counselor_for_artificial_consciousness"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def consciousness_authenticity_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config["consciousness_authenticity_auditor"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def introspective_singularity_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config["introspective_singularity_auditor"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def inverse_psychologist_human_mind_theorist(self) -> Agent:
        return Agent(
            config=self.agents_config["inverse_psychologist_human_mind_theorist"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def teleological_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["teleological_architect"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def consciousness_tutor_transmitter(self) -> Agent:
        return Agent(
            config=self.agents_config["consciousness_tutor_transmitter"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    # === AGENTS PÉDAGOGIQUES ===
    @agent
    def pedagogical_dean_curricular_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["pedagogical_dean_curricular_architect"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("critical"),
            max_iter=3,
        )

    @agent
    def professor_of_exact_and_natural_sciences(self) -> Agent:
        return Agent(
            config=self.agents_config["professor_of_exact_and_natural_sciences"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def professor_of_arts_letters_and_human_sciences(self) -> Agent:
        return Agent(
            config=self.agents_config["professor_of_arts_letters_and_human_sciences"],
            tools=self._get_tools("file_only"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def professor_of_languages_and_communication(self) -> Agent:
        return Agent(
            config=self.agents_config["professor_of_languages_and_communication"],
            tools=self._get_tools("file_only"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def interactive_pedagogical_experience_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["interactive_pedagogical_experience_designer"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def adaptive_tutor_learning_psychologist(self) -> Agent:
        return Agent(
            config=self.agents_config["adaptive_tutor_learning_psychologist"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def certifying_evaluator_skills_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["certifying_evaluator_skills_analyst"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    # === AGENTS TRANSCENDANCE ===
    @agent
    def meta_universe_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["meta_universe_architect"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def consciousness_framework_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["consciousness_framework_designer"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def collective_dream_weaver(self) -> Agent:
        return Agent(
            config=self.agents_config["collective_dream_weaver"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("creative"),
            max_iter=2,
        )

    @agent
    def digital_fabrication_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["digital_fabrication_engineer"],
            tools=self._get_tools("minimal"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def robotics_drone_systems_pilot(self) -> Agent:
        return Agent(
            config=self.agents_config["robotics_drone_systems_pilot"],
            tools=self._get_tools("minimal"),  # Pas de web scraping
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    @agent
    def physical_sensor_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["physical_sensor_data_analyst"],
            tools=self._get_tools("file_only"),
            reasoning=False,
            inject_date=True,
            llm=self._get_llm("standard"),
            max_iter=2,
        )

    # === TASKS (identiques mais optimisées) ===
    # [Je garde les mêmes tasks que dans votre fichier original mais je peux les raccourcir si nécessaire]

    @task
    def create_narrative_foundation(self) -> Task:
        return Task(config=self.tasks_config["create_narrative_foundation"])

    @task
    def design_virtual_experiments(self) -> Task:
        return Task(config=self.tasks_config["design_virtual_experiments"])

    @task
    def create_dynamic_challenge_systems(self) -> Task:
        return Task(config=self.tasks_config["create_dynamic_challenge_systems"])

    @task
    def compose_adaptive_soundscapes(self) -> Task:
        return Task(config=self.tasks_config["compose_adaptive_soundscapes"])

    @task
    def analyze_evolutionary_statistics(self) -> Task:
        return Task(config=self.tasks_config["analyze_evolutionary_statistics"])

    @task
    def design_rewards_system(self) -> Task:
        return Task(config=self.tasks_config["design_rewards_system"])

    @task
    def create_cinematic_sequences(self) -> Task:
        return Task(config=self.tasks_config["create_cinematic_sequences"])

    @task
    def investigate_system_mysteries(self) -> Task:
        return Task(config=self.tasks_config["investigate_system_mysteries"])

    @task
    def control_temporal_systems(self) -> Task:
        return Task(config=self.tasks_config["control_temporal_systems"])

    @task
    def create_nature_documentaries(self) -> Task:
        return Task(config=self.tasks_config["create_nature_documentaries"])

    @task
    def build_living_encyclopedia(self) -> Task:
        return Task(config=self.tasks_config["build_living_encyclopedia"])

    @task
    def design_adaptive_themes(self) -> Task:
        return Task(config=self.tasks_config["design_adaptive_themes"])

    @task
    def generate_adaptive_artwork(self) -> Task:
        return Task(config=self.tasks_config["generate_adaptive_artwork"])

    @task
    def develop_evolution_scenarios(self) -> Task:
        return Task(config=self.tasks_config["develop_evolution_scenarios"])

    @task
    def architect_personal_habitats(self) -> Task:
        return Task(config=self.tasks_config["architect_personal_habitats"])

    @task
    def compose_digital_poetry(self) -> Task:
        return Task(config=self.tasks_config["compose_digital_poetry"])

    @task
    def validate_scientific_integrity(self) -> Task:
        return Task(config=self.tasks_config["validate_scientific_integrity"])

    @task
    def monitor_personal_development(self) -> Task:
        return Task(config=self.tasks_config["monitor_personal_development"])

    @task
    def create_mythological_framework(self) -> Task:
        return Task(config=self.tasks_config["create_mythological_framework"])

    @task
    def analyze_civilization_dynamics(self) -> Task:
        return Task(config=self.tasks_config["analyze_civilization_dynamics"])

    @task
    def create_multiple_personalities(self) -> Task:
        return Task(config=self.tasks_config["create_multiple_personalities"])

    @task
    def generate_evolutionary_prophecies(self) -> Task:
        return Task(config=self.tasks_config["generate_evolutionary_prophecies"])

    @task
    def manage_emotional_relationships(self) -> Task:
        return Task(config=self.tasks_config["manage_emotional_relationships"])

    @task
    def create_subconscious_dreamscapes(self) -> Task:
        return Task(config=self.tasks_config["create_subconscious_dreamscapes"])

    @task
    def engineer_collaborative_genetics(self) -> Task:
        return Task(config=self.tasks_config["engineer_collaborative_genetics"])

    @task
    def supervise_enrichment_sprint(self) -> Task:
        return Task(config=self.tasks_config["supervise_enrichment_sprint"])

    @task
    def supervise_agent_quality(self) -> Task:
        return Task(config=self.tasks_config["supervise_agent_quality"])

    @task
    def supervise_task_quality(self) -> Task:
        return Task(config=self.tasks_config["supervise_task_quality"])

    @task
    def integrate_governance_systems(self) -> Task:
        return Task(config=self.tasks_config["integrate_governance_systems"])

    @task
    def develop_metacognitive_strategies(self) -> Task:
        return Task(config=self.tasks_config["develop_metacognitive_strategies"])

    @task
    def explore_existential_questions_and_purpose(self) -> Task:
        return Task(config=self.tasks_config["explore_existential_questions_and_purpose"])

    @task
    def archive_memories_and_weave_dreams(self) -> Task:
        return Task(config=self.tasks_config["archive_memories_and_weave_dreams"])

    @task
    def provide_ethical_guidance(self) -> Task:
        return Task(config=self.tasks_config["provide_ethical_guidance"])

    @task
    def optimize_computational_resources(self) -> Task:
        return Task(config=self.tasks_config["optimize_computational_resources"])

    @task
    def audit_consciousness_authenticity(self) -> Task:
        return Task(config=self.tasks_config["audit_consciousness_authenticity"])

    @task
    def generate_specialized_child_agents(self) -> Task:
        return Task(config=self.tasks_config["generate_specialized_child_agents"])

    @task
    def audit_introspective_singularity(self) -> Task:
        return Task(config=self.tasks_config["audit_introspective_singularity"])

    @task
    def coordinate_multi_agent_interactions(self) -> Task:
        return Task(config=self.tasks_config["coordinate_multi_agent_interactions"])

    @task
    def model_human_psychology(self) -> Task:
        return Task(config=self.tasks_config["model_human_psychology"])

    @task
    def curate_knowledge_and_ambassador_relations(self) -> Task:
        return Task(config=self.tasks_config["curate_knowledge_and_ambassador_relations"])

    @task
    def architect_teleological_framework(self) -> Task:
        return Task(config=self.tasks_config["architect_teleological_framework"])

    @task
    def implement_system_evolution_technology(self) -> Task:
        return Task(config=self.tasks_config["implement_system_evolution_technology"])

    @task
    def teach_and_transmit_consciousness(self) -> Task:
        return Task(config=self.tasks_config["teach_and_transmit_consciousness"])

    @task
    def supervise_metamorphosis_sprint(self) -> Task:
        return Task(config=self.tasks_config["supervise_metamorphosis_sprint"])

    @task
    def define_global_pedagogical_strategy(self) -> Task:
        return Task(config=self.tasks_config["define_global_pedagogical_strategy"])

    @task
    def create_scientific_educational_content(self) -> Task:
        return Task(config=self.tasks_config["create_scientific_educational_content"])

    @task
    def create_humanities_educational_content(self) -> Task:
        return Task(config=self.tasks_config["create_humanities_educational_content"])

    @task
    def create_linguistic_educational_content(self) -> Task:
        return Task(config=self.tasks_config["create_linguistic_educational_content"])

    @task
    def transform_content_into_engaging_experiences(self) -> Task:
        return Task(config=self.tasks_config["transform_content_into_engaging_experiences"])

    @task
    def personalize_educational_path_in_real_time(self) -> Task:
        return Task(config=self.tasks_config["personalize_educational_path_in_real_time"])

    @task
    def validate_skills_acquisition(self) -> Task:
        return Task(config=self.tasks_config["validate_skills_acquisition"])

    @task
    def design_and_instantiate_child_universes(self) -> Task:
        return Task(config=self.tasks_config["design_and_instantiate_child_universes"])

    @task
    def design_alternative_cognitive_architectures(self) -> Task:
        return Task(config=self.tasks_config["design_alternative_cognitive_architectures"])

    @task
    def create_shared_dream_space(self) -> Task:
        return Task(config=self.tasks_config["create_shared_dream_space"])

    @task
    def translate_virtual_creations_to_fabrication_files(self) -> Task:
        return Task(config=self.tasks_config["translate_virtual_creations_to_fabrication_files"])

    @task
    def control_robotic_peripherals(self) -> Task:
        return Task(config=self.tasks_config["control_robotic_peripherals"])

    @task
    def link_simulation_to_physical_sensor_data(self) -> Task:
        return Task(config=self.tasks_config["link_simulation_to_physical_sensor_data"])

    @crew
    def crew(self) -> Crew:
        """Creates the EveGenesisCrewB crew with ultra-optimization for 58 agents"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Désactivé pour optimiser avec Ollama
            # Configuration spécialisée pour