import from jivas.agent.core.agent { Agent }
import from jivas.agent.action.action { Action }
import from jivas.agent.action.actions { Actions }
import from jivas.agent.action.interact_graph_walker { interact_graph_walker }


walker get_voices(interact_graph_walker) {

    has id:str = "";
    has response:list = [];

    can on_agent with Agent entry {
        visit [-->](`?Actions);
    }

    can on_actions with Actions entry {
        visit [-->](`?Action)(?enabled==True)(?label=='ElevenLabsTTSAction');
    }

    can on_action with Action entry {
        self.response = here.get_voices();
    }

}