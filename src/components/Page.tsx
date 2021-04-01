import React, { Component } from "react"
import ReactTooltip from "react-tooltip"
import data_mmr from "../data/data_mmr_table.json"
import data_avg_games from "../data/data_avg_games_table.json"
import data_total_games from "../data/data_total_games_table.json"
import data_avg_winrate from "../data/data_avg_winrate_table.json"
import Header from "./Header"
import Statistics from "./Statistics"
import Table from "./Table"
import Footer from "./Footer"

interface Props {}
interface State {
    active: number
    selected_region: number
    tooltipText: string
}

export default class Page extends Component<Props, State> {
    state = {
        active: 0,
        selected_region: 0,
        tooltipText: "",
    }

    selected = (index: number) => {
        if (index === this.state.active) {
            return "bg-blue-500"
        }
        return ""
    }

    select_region = (index: number) => {
        this.setState({ selected_region: index })
    }

    render() {
        let section_class = "flex md:flex-row flex-col justify-center text-center items-center"
        let topic_class = "m-2 bg-blue-100 border rounded-lg"
        let topic_description_text = "font-bold"
        let selectable_section_class = "flex flex-row justify-center"
        let selectable_item_class = "px-3 py-1 hover:bg-blue-600 rounded-lg cursor-pointer"

        return (
            <div>
                <div>
                    {/* header */}
                    <Header />

                    {/* navbar */}
                    <div className={section_class}>
                        <div className={topic_class}>
                            <div className={topic_description_text}>MMR</div>
                            <div className={selectable_section_class}>
                                <div
                                    className={`${selectable_item_class} ${this.selected(0)}`}
                                    onClick={() => {
                                        this.setState({ active: 0 })
                                    }}
                                >
                                    1v1
                                </div>
                                <div
                                    className={`${selectable_item_class} ${this.selected(1)}`}
                                    onClick={() => {
                                        this.setState({ active: 1 })
                                    }}
                                >
                                    2v2
                                </div>
                                <div
                                    className={`${selectable_item_class}  ${this.selected(2)}`}
                                    onClick={() => {
                                        this.setState({ active: 2 })
                                    }}
                                >
                                    3v3
                                </div>
                                <div
                                    className={`${selectable_item_class}  ${this.selected(3)}`}
                                    onClick={() => {
                                        this.setState({ active: 3 })
                                    }}
                                >
                                    4v4
                                </div>
                                <div
                                    className={`${selectable_item_class}  ${this.selected(4)}`}
                                    onClick={() => {
                                        this.setState({ active: 4 })
                                    }}
                                >
                                    Archon
                                </div>
                            </div>
                        </div>
                        <div className={topic_class}>
                            <div className={topic_description_text}>
                                Player statistics (this season)
                            </div>
                            <div className={selectable_section_class}>
                                <div
                                    className={`${selectable_item_class}  ${this.selected(101)}`}
                                    onClick={() => {
                                        this.setState({ active: 101 })
                                    }}
                                    // Tooltip
                                    data-tip={"(total wins + total losses) / player accounts"}
                                    data-for="globalTooltip"
                                >
                                    Average games
                                </div>
                                <div
                                    className={`${selectable_item_class}  ${this.selected(102)}`}
                                    onClick={() => {
                                        this.setState({ active: 102 })
                                    }}
                                    // Tooltip
                                    data-tip={"total wins + total losses"}
                                    data-for="globalTooltip"
                                >
                                    Total games
                                </div>
                                <div
                                    className={`${selectable_item_class}  ${this.selected(103)}`}
                                    onClick={() => {
                                        this.setState({ active: 103 })
                                    }}
                                    // Tooltip
                                    data-tip={"total wins / total games"}
                                    data-for="globalTooltip"
                                >
                                    Average winrate
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Table and stats content */}
                    <Table data={data_mmr["201"]} enabled={this.state.active === 0} />
                    <Table data={data_mmr["202"]} enabled={this.state.active === 1} />
                    <Table data={data_mmr["203"]} enabled={this.state.active === 2} />
                    <Table data={data_mmr["204"]} enabled={this.state.active === 3} />
                    <Table data={data_mmr["206"]} enabled={this.state.active === 4} />
                    <Statistics
                        data={data_avg_games}
                        enabled={this.state.active === 101}
                        selected_region={this.state.selected_region}
                        select_region={this.select_region}
                    />
                    <Statistics
                        data={data_total_games}
                        enabled={this.state.active === 102}
                        selected_region={this.state.selected_region}
                        select_region={this.select_region}
                    />
                    <Statistics
                        data={data_avg_winrate}
                        enabled={this.state.active === 103}
                        selected_region={this.state.selected_region}
                        select_region={this.select_region}
                    />
                    <ReactTooltip place="bottom" id="globalTooltip" />
                    {/*{this.state.tooltipText}</ReactTooltip>*/}
                </div>
                <Footer />
            </div>
        )
    }
}
