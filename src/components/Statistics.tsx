import React, { Component } from "react"

interface Props {
    data: { [name: string]: Array<string[]> }
    enabled: boolean
    selected_region: number
    select_region: (index: number) => void
}
interface State {}

export default class Statistics extends Component<Props, State> {
    selected = (index: number) => {
        if (index === this.props.selected_region) {
            return "bg-blue-500"
        }
        return ""
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
        let selector_row = "flex flex-row m-2 bg-blue-100 border rounded-lg"
        let selectable_item_class = "px-3 py-1 hover:bg-blue-600 rounded-lg cursor-pointer"

        let content_class = ""
        let hidden_class = "hidden"

        let table_us = this.format_table(this.props.data["us"])
        let table_eu = this.format_table(this.props.data["eu"])
        let table_kr = this.format_table(this.props.data["kr"])

        return (
            <div className={`flex flex-col items-center ${this.props.enabled ? "" : "hidden"}`}>
                <div className={selector_row}>
                    <div
                        className={`${selectable_item_class} ${this.selected(0)}`}
                        onClick={() => {
                            this.props.select_region(0)
                        }}
                    >
                        Americas
                    </div>
                    <div
                        className={`${selectable_item_class} ${this.selected(1)}`}
                        onClick={() => {
                            this.props.select_region(1)
                        }}
                    >
                        Europe
                    </div>
                    <div
                        className={`${selectable_item_class} ${this.selected(2)}`}
                        onClick={() => {
                            this.props.select_region(2)
                        }}
                    >
                        Korea
                    </div>
                </div>
                <div>
                    <div
                        className={`${content_class} ${
                            this.props.selected_region !== 0 ? hidden_class : null
                        }`}
                    >
                        {table_us}
                    </div>
                    <div
                        className={`${content_class} ${
                            this.props.selected_region !== 1 ? hidden_class : null
                        }`}
                    >
                        {table_eu}
                    </div>
                    <div
                        className={`${content_class} ${
                            this.props.selected_region !== 2 ? hidden_class : null
                        }`}
                    >
                        {table_kr}
                    </div>
                </div>
            </div>
        )
    }
}
