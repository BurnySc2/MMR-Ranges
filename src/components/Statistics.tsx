import React, { Component } from "react"

interface Props {
    data: { [name: string]: Array<string[]> }
    enabled: boolean
}
interface State {
    active: number
}

export default class Statistics extends Component<Props, State> {
    state = {
        active: 0,
    }

    format_table = (table: Array<string[]>) => {
        let table_class = "table-fixed"
        let table_row_class = "hover:bg-gray-400"
        let table_header_class = "p-4"
        let table_cell_class = "px-4 py-2 text-center font-semibold border-t-2"

        let table_formatted = table.map((row_data: string[], index: number) => {
            let row = row_data.map((entry: string, index2: number) => {
                if (index === 0) {
                    return <th className={table_header_class}>{entry}</th>
                } else {
                    return <td className={table_cell_class}>{entry}</td>
                }
            })
            return <tr className={table_row_class}>{row}</tr>
        })
        return <table className={table_class}>{table_formatted}</table>
    }

    render() {
        if (!this.props.enabled) {
            return <div></div>
        }
        let selector_row = "flex flex-row m-2 bg-blue-100 border rounded-lg"
        let selectable_item_class = "px-3 py-1 hover:bg-blue-600 rounded-lg cursor-pointer"
        let selected_class = "bg-blue-500"

        let content_class = ""
        let hidden_class = "hidden"

        let table_us = this.format_table(this.props.data["us"])
        let table_eu = this.format_table(this.props.data["eu"])
        let table_kr = this.format_table(this.props.data["kr"])

        return (
            <div className="flex flex-col items-center">
                <div className={selector_row}>
                    <div
                        className={`${selectable_item_class} ${
                            this.state.active === 0 ? selected_class : null
                        }`}
                        onClick={() => {
                            this.setState({ active: 0 })
                        }}
                    >
                        Americas
                    </div>
                    <div
                        className={`${selectable_item_class} ${
                            this.state.active === 1 ? selected_class : null
                        }`}
                        onClick={() => {
                            this.setState({ active: 1 })
                        }}
                    >
                        Europe
                    </div>
                    <div
                        className={`${selectable_item_class} ${
                            this.state.active === 2 ? selected_class : null
                        }`}
                        onClick={() => {
                            this.setState({ active: 2 })
                        }}
                    >
                        Korea
                    </div>
                </div>
                <div>
                    <div
                        className={`${content_class} ${
                            this.state.active !== 0 ? hidden_class : null
                        }`}
                    >
                        {table_us}
                    </div>
                    <div
                        className={`${content_class} ${
                            this.state.active !== 1 ? hidden_class : null
                        }`}
                    >
                        {table_eu}
                    </div>
                    <div
                        className={`${content_class} ${
                            this.state.active !== 2 ? hidden_class : null
                        }`}
                    >
                        {table_kr}
                    </div>
                </div>
            </div>
        )
    }
}
