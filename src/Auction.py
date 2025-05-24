from AuctionAllocation import AllocationMechanism
from Bidder import Bidder

import numpy as np

from BidderAllocation import OracleAllocator
from Models import sigmoid

class Auction:
    ''' Base class for auctions '''
    def __init__(self, rng, allocation, agents, agent2items, agents2item_values, 
                 max_slots, embedding_size, embedding_var, obs_embedding_size, 
                 num_participants_per_round, fixed_cvr: float, fixed_sales_revenue_per_conversion: float):
        self.rng = rng
        self.allocation = allocation
        self.agents = agents
        self.max_slots = max_slots
        self.revenue = .0

        self.agent2items = agent2items
        self.agents2item_values = agents2item_values

        self.embedding_size = embedding_size
        self.embedding_var = embedding_var

        self.obs_embedding_size = obs_embedding_size

        self.num_participants_per_round = num_participants_per_round

        # New parameters for CVR and sales revenue
        self.fixed_cvr = fixed_cvr
        self.fixed_sales_revenue_per_conversion = fixed_sales_revenue_per_conversion

    def simulate_opportunity(self):
        # Sample the number of slots uniformly between [1, max_slots]
        num_slots = self.rng.integers(1, self.max_slots + 1)

        # Sample a true context vector
        true_context = np.concatenate((self.rng.normal(0, self.embedding_var, size=self.embedding_size), [1.0]))

        # Mask true context into observable context
        obs_context = np.concatenate((true_context[:self.obs_embedding_size], [1.0]))

        # At this point, the auctioneer solicits bids from
        # the list of bidders that might want to compete.
        bids = []
        CTRs = []
        participating_agents_idx = self.rng.choice(len(self.agents), self.num_participants_per_round, replace=False)
        participating_agents = [self.agents[idx] for idx in participating_agents_idx]
        for agent in participating_agents:
            # Get the bid and the allocated item
            if isinstance(agent.allocator, OracleAllocator):
                bid, item = agent.bid(true_context)
            else:
                bid, item = agent.bid(obs_context)
            bids.append(bid)
            # Compute the true CTRs for items in this agent's catalogue
            true_CTR = sigmoid(true_context @ self.agent2items[agent.name].T)
            agent.logs[-1].set_true_CTR(np.max(true_CTR * self.agents2item_values[agent.name]), true_CTR[item])
            CTRs.append(true_CTR[item])
        bids = np.array(bids)
        CTRs = np.array(CTRs)

        # Now we have bids, we need to somehow allocate slots
        # "second_prices" tell us how much lower the winner could have gone without changing the outcome
        # winner_indices_in_bids are indices relative to the `bids` array (and thus `participating_agents`)
        winner_indices_in_bids, slot_prices, slot_second_prices = self.allocation.allocate(bids, num_slots)

        # Bidders only obtain value when they get their outcome
        # Either P(view), P(click | view, ad), P(conversion | click, view, ad)
        # For now, look at P(click | ad) * P(view)
        # Determine click outcomes for the winning slots
        clicks_on_winning_slots = self.rng.binomial(1, CTRs[winner_indices_in_bids])

        # Store details for winners to process revenue and charge them correctly.
        # This map stores the outcome for the specific slot an agent won.
        # Key: agent_idx_in_participating_agents, Value: (price, second_price, click_outcome)
        winning_agent_slot_details = {}
        for k_slot in range(len(winner_indices_in_bids)):
            agent_idx_for_slot = winner_indices_in_bids[k_slot]
            price_for_slot = slot_prices[k_slot]
            second_price_for_slot = slot_second_prices[k_slot]
            click_for_slot = bool(clicks_on_winning_slots[k_slot])
            
            # If an agent could win multiple slots, this would take the last one.
            # Assuming an agent wins at most one slot relevant to their single log entry.
            if agent_idx_for_slot not in winning_agent_slot_details: # Prioritize first slot won if multiple
                winning_agent_slot_details[agent_idx_for_slot] = (price_for_slot, second_price_for_slot, click_for_slot)
                self.revenue += price_for_slot # Accumulate revenue for this won slot

        # Update logs for all participating agents (winners and losers)
        for i, agent in enumerate(participating_agents):
            conversion_occurred = False
            current_sales_revenue = 0.0

            if i in winning_agent_slot_details:  # Agent 'i' won a slot
                price, second_price, click_outcome = winning_agent_slot_details[i]
                agent.charge(price, second_price, click_outcome)  # Updates agent's log with win, price, and click
                
                if click_outcome:  # Conversion can only happen if there was a click
                    conversion_occurred = self.rng.random() < self.fixed_cvr
                    if conversion_occurred:
                        current_sales_revenue = self.fixed_sales_revenue_per_conversion
            else:  # Agent 'i' lost
                # Explicitly set outcome for losers in their log.
                # ImpressionOpportunity defaults (won=False, outcome=0, price=0.0) are set during agent.bid()
                # Calling set_price_outcome ensures these are explicitly recorded as such.
                agent.logs[-1].set_price_outcome(price=0.0, second_price=0.0, outcome=False, won=False)
            
            # Set conversion details for every participating agent's log entry
            agent.logs[-1].set_conversion_details(conversion_occurred, current_sales_revenue)

    def clear_revenue(self):
        self.revenue = 0.0
